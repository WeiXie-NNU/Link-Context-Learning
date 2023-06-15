from ..root import (
    DATASETS,
    QUESTION_PLACEHOLDER,
    IMAGE_PLACEHOLDER,
    BOXES_PLACEHOLDER,
)
from ..utils import MInstrDataset


def prepare_sentence(sent):
    ret_str = []
    ret_box_seq = []
    for word in sent:
        if isinstance(word, list):
            ret_str.append(BOXES_PLACEHOLDER)
            ret_box_seq.append(word)
    return " ".join(ret_str), ret_box_seq


def prepare_choice(pack_choices, label_index, *, options='ABCDEFG'):
    ret_str = []
    ret_box_seq = []
    for pack, op in zip(pack_choices, options):
        ret_str.append(f"({op}) {pack[0]}")
        ret_box_seq.append(pack[1])
    ret_pack = (" ".join(ret_str), ret_box_seq)
    label_choice = f"The answer is ({options[label_index]})."
    return ret_pack, (label_choice, [])


def merge(packs, *, prefixs, postfixs=None):
    if postfixs is None:
        postfixs = ['' for _ in range(len(packs))]
    assert len(packs) == len(prefixs) == len(postfixs), f"{len(packs)},{len(prefixs)},{len(postfixs)}"
    ret_str = []
    ret_box_seq = []
    for pack, prefix in zip(packs, prefixs):
        ret_str.append(prefix)
        ret_str.append(pack[0])
        ret_box_seq.append(pack[1])
    return " ".join(ret_str), ret_box_seq


@DATASETS.register_module()
class VCRDataset(MInstrDataset):
    def __init__(self, *args, version, **kwargs):
        super().__init__(*args, **kwargs, placeholders=(IMAGE_PLACEHOLDER, QUESTION_PLACEHOLDER))
        self.version = version
        assert version in [
            'q-a', 'q-ra',
            'qc-a', 'qc-ra', 'qc-rac',  # for evaluation: A
            'qa-r', 'q-a-q-r',
            'qac-r', 'qc-a-qc-r',  # for evaluation: R
        ]
        # for evaluation:
        # A: 'qc-a' 'qc-ra' 'qc-rac'
        # R: 'qac-r' 'qc-a-qc-r'

    def __getitem__(self, index):
        item = self.get_raw_item(index)
        image = self.get_image(item['img_fn'])

        boxes = item['boxes']

        question = item['question']
        answer_choices = item['answer_choices']
        rationale_choices = item['rationale_choices']
        answer_label = item['answer_label']
        rationale_label = item['rationale_label']

        question_pack = prepare_sentence(question)
        answer_pack_choices = [prepare_sentence(_) for _ in answer_choices]
        rationale_pack_choices = [prepare_sentence(_) for _ in rationale_choices]

        answer_choices_pack, answer_choice = prepare_choice(answer_pack_choices, answer_label)
        rationale_choices_pack, rationale_choice = prepare_choice(rationale_pack_choices, answer_label)
        answer_gold_pack = answer_pack_choices[answer_label]
        rationale_gold_pack = rationale_pack_choices[rationale_label]

        version = self.version
        if version == 'q-a':
            final_packs = [
                merge([question_pack], prefixs=['QUESTION:'], ),
                answer_gold_pack,
            ]
        elif version == 'q-ra':
            final_packs = [
                merge([question_pack], prefixs=['QUESTION:'], ),
                merge([rationale_gold_pack, answer_gold_pack], prefixs=['', '']),
            ]
        elif version == 'qc-a':
            final_packs = [
                merge([question_pack, answer_choices_pack], prefixs=['QUESTION:', '\nOPTIONS:'], postfixs=['', 'You should decide on the best choice and output the corresponding letter.']),
                answer_choice,
            ]
        elif version == 'qc-ra':
            final_packs = [
                merge([question_pack, answer_choices_pack], prefixs=['QUESTION:', '\nOPTIONS:'], postfixs=['', 'You should decide on the best choice and output the corresponding letter.']),
                merge([rationale_gold_pack, answer_choice], prefixs=['', '']),
            ]
        elif version == 'qc-rac':
            final_packs = [
                merge([question_pack, answer_choices_pack], prefixs=['QUESTION:', '\nOPTIONS:'], postfixs=['', 'You should decide on the best choice and output the corresponding letter.']),
                merge([rationale_gold_pack, answer_gold_pack, answer_choice], prefixs=['', '', '']),
            ]
        elif version == 'qa-r':
            final_packs = [
                merge([question_pack, answer_gold_pack], prefixs=['QUESTION:', '\nANSWER:'], postfixs=['', 'You should explain the reason for the above answer.']),
                rationale_gold_pack,
            ]
        elif version == 'qac-r':
            final_packs = [
                merge([question_pack, answer_gold_pack, rationale_choices_pack], prefixs=['QUESTION:', '\nANSWER:', '\nRATIONALE OPTIONS:'], postfixs=['', '', 'You should decide on the best choice that explains the above answer and output the corresponding letter.']),
                rationale_choice,
            ]
        elif version == 'q-a-q-r':
            final_packs = [
                merge([question_pack], prefixs=['QUESTION:'], ),
                answer_gold_pack,
                ('You should explain the reason for the above answer.', ()),
                rationale_gold_pack,
            ]
        elif version == 'qc-a-qc-r':
            final_packs = [
                merge([question_pack, answer_choices_pack], prefixs=['QUESTION:', '\nOPTIONS:'], postfixs=['', 'You should decide on the best choice and output the corresponding letter.']),
                answer_choice,
                merge([rationale_choices_pack], prefixs=['RATIONALE OPTIONS:'], postfixs=['You should decide on the best choice that explains the above answer and output the corresponding letter.']),
                rationale_choice,
            ]
        else:
            assert False

        conversations = []
        roles = ['human', 'gpt']
        for idx, pack in enumerate(final_packs):
            conversations.append({
                'from': roles[idx % 2],
                'value': pack[0],
                'boxes_seq': pack[1],
            })
        conversations[0]['value'] = self.get_template().replace(QUESTION_PLACEHOLDER, conversations[0]['value'])

        ret = {
            'image': image,
            'target': {'boxes': boxes},
            'conversations': conversations,
        }
        return ret
