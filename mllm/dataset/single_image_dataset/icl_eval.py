import imp
import re
import sys
import logging
import warnings
import os
import os.path as osp
import jsonlines
import random
from typing import Dict, Any, Sequence
from numpy import real

import torch
from .imagenet import ImageNetDataset

from .. import BaseComputeMetrics
from ..root import (
    DATASETS,
    METRICS,
    QUESTION_PLACEHOLDER,
    IMAGE_PLACEHOLDER,
)


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    datefmt="%m/%d/%Y %H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout), ],
)


@DATASETS.register_module()
class ICLEvalDataset(ImageNetDataset):
    def __init__(self, sample_per_class = 0, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sample_per_class = sample_per_class
        self.data_map = self._rearrange()

    def __len__(self):
        return len(self.data_map)

    def _rearrange(self):
        # Map dataloader index to self.data, according to class_idx and sample_idx
        data_map = []
        for cls_idx, item in enumerate(self.data):
            test_samples = item['test_samples']
            for sample_idx, sample in enumerate(test_samples):
                # sample_per_class = 0: all samples evaluation
                if sample_idx == self.sample_per_class and \
                    self.sample_per_class > 0:
                    break
                data_map.append([cls_idx, sample_idx])
        return data_map        

    def get_samples(self, index, shot):
        cls_idx, sample_idx = self.data_map[index]
        item = self.get_raw_item(cls_idx)
        class_id = item["class_id"]
        class_name = item["class_name"]
        context_samples = item["context_samples"]
        test_samples = item['test_samples']

        test_img = self.get_image(test_samples[sample_idx])
        context_imgs = []
        for i in range(shot):
            context_imgs.append(self.get_image(context_samples[i]))
        return class_name, context_imgs, test_img
         

    def get_ret(self, image, question, answer):
        ret = {
            'image': image,
            'conversations': [
                {
                    'from': 'human',
                    'value': question,
                },
                {
                    'from': 'gpt',
                    'value': f"The answer is {answer}.",
                },
            ]
        }
        return ret

    def __get_icl_item__(self, index, shot):
        ret_list = []
        question = 'What is the class of the image <image>?'
        class_name, context_imgs, test_img = self.get_samples(index, shot)
        # context sample
        for i in range(shot):
            ret_list.append(self.get_ret(context_imgs[i], question=question, answer=class_name))
        
        # eval sample
        ret_list.append(self.get_ret(test_img, question=question, answer=class_name))
        return ret_list

ANS_EXTRACT_PAT = re.compile(r'(?:The answer is (.+?)\.)')

@METRICS.register_module()
class ICLComputeMetrics(BaseComputeMetrics):
    def extract_ans(self, string: str, mode: str):
        try:
            if mode == "pred":
                found = ANS_EXTRACT_PAT.findall(string.strip())
                if len(found) != 1:
                    return None
                return found[0].strip()
            elif mode == "target":
                found = string.split("ASSISTANT:")[-1].split("</s>")[0].replace("The answer is", "").replace(".", "").strip()
                return found
        except (IndexError, AttributeError):
            return None

    def calculate_metric(self, preds: Sequence[str], targets: Sequence[str]) -> Dict[str, Any]:
        correct = 0
        failed = 0
        target_failed = 0
        for pred, target in zip(preds, targets):
            extract_pred = self.extract_ans(pred, mode = "pred")
            extract_target = self.extract_ans(target, mode = "target")
            if extract_target is None:
                target_failed += 1
                logger.warning(f"failed to extract ans from target. maybe the response string is truncated: {target}.")
                continue
            if extract_pred is None:
                failed += 1
            if extract_pred == extract_target:
                correct += 1
        return {
            'accuracy': 1.0 * correct / len(targets),
            'target_failed': target_failed,
            'failed': failed,
        }