_base_ = ['_base_/dataset/rec_ref3_reverse.py', '_base_/model/llava_v1_7b.py', '_base_/train/llava_fsdp.py']

training_args = dict(
    output_dir='/mnt/lustre/share_data/chenkeqin/exp_unify_mllm/{{fileBasenameNoExtension}}',
)

data_args = dict(

    train=dict(
        caption_min_words=8,
    ),
    validation=dict(
        caption_min_words=8,
    ),
    test=dict(
        caption_min_words=8,
    ),
)