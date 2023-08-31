import imp
import sys
import logging
import warnings
import os
import os.path as osp
import jsonlines
import random

from ..utils import MInstrDataset
from .. import BaseComputeMetrics

from ..root import (
    DATASETS,
    METRICS,
    QUESTION_PLACEHOLDER,
    IMAGE_PLACEHOLDER,
    EXPR_PLACEHOLDER,
    MAPPING_DICT,
)
LABEL_PLACEHOLDER = "<label>"

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    datefmt="%m/%d/%Y %H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout), ],
)


@DATASETS.register_module()
class LCLDataset(MInstrDataset):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, placeholders=(IMAGE_PLACEHOLDER, EXPR_PLACEHOLDER))
        self.data = self._get_annos(self.filename)
        self.cls_neg_label = None
        self.cls_idx = None
        self.cls_name = None

    def _get_annos(self, filename):
        cls_metas = []
        with jsonlines.open(filename) as reader:
            for metas in reader:
                cls_metas.append(metas)
        return cls_metas

    def get_raw_item(self, index):
        return self.data[index]

    def get_ret(self, image, question, answer, conv_mode=None):
        ret = {
            'image': image,
            'conversations': [
                {
                    'from': 'human',
                    'value': question,
                },
                {
                    'from': 'gpt',
                    'value': f"{answer}",
                },
            ]
        }
        if conv_mode is not None:
            ret['mode'] = conv_mode
        return ret

    def get_samples(self, index, mode="cls_positive"):
        assert mode in ['cls_positive','cls_negative', 'neighbors']

        item = self.get_raw_item(index)
        samples = item['samples']
        neighbors = item['neighbors']
        
        if mode == "cls_positive":
            # current class image and label
            label = item['class_name'].lower()
            sample = random.choice(samples)
        elif mode == "cls_negative":
            # current class image, random neighbor label
            if self.cls_neg_label:
                label = self.cls_neg_label
            else:
                metas = random.choice(neighbors)
                label = metas[1].lower()
                self.cls_neg_label = label
            sample = random.choice(samples)
        elif mode == "neighbors":
            # random neighbor image and label
            metas = random.choice(neighbors)
            label = metas[1].lower()
            sample = metas[2]
        else:
            raise NotImplementedError

        image = self.get_image(sample)
        return image, label

    def get_samples_same_cls(self, index, mode="cls_negative"):
        assert mode in ['cls_negative', 'neighbors']

        item = self.get_raw_item(index)
        samples = item['samples']
        neighbors = item['neighbors']

        if mode == "cls_negative":
            # current class image, random neighbor label
            if self.cls_neg_label:
                label = self.cls_neg_label
            else:
                metas = random.choice(neighbors)
                label = metas[1].lower()
                self.cls_neg_label = label
            sample = random.choice(samples)
        elif mode == "neighbors":
            if self.cls_idx:
                item_neighbor = self.get_raw_item(int(MAPPING_DICT[self.cls_idx]))
                samples_neighbor = item_neighbor['samples']
                samples = samples_neighbor
                sample = random.choice(samples)
                label = self.cls_name.lower()
            else:
                sample_weight = list(range(len(neighbors),0,-1))
                metas = random.choices(neighbors,weights=sample_weight)
                metas = metas[0]

                self.cls_idx = metas[0]
                self.cls_name = metas[1]
                label = metas[1].lower()
                sample = metas[2]
        else:
            raise NotImplementedError

        image = self.get_image(sample)
        return image, label

    def __getitem__(self, index):
        raise NotImplementedError

    def __get_icl_item__(self, index, shot):
        raise NotImplementedError

@METRICS.register_module()
class LCLComputeMetrics(BaseComputeMetrics):
    def extract_ans(self, string: str):
        try:
            found = string.split("ASSISTANT:")[-1].split("</s>")[0].replace("The answer is", "").replace('there is', '').replace('in the image', '').replace(".", "").strip().lower()
            return found
        except (IndexError, AttributeError):
            return None