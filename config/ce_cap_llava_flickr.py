_base_ = ['_base_/dataset/complex_event_cap.py', '_base_/model/llava_v1_7b.py', '_base_/train/eval.py']

training_args = dict(
    output_dir='/mnt/lustre/share_data/chenkeqin/exp_unify_mllm_on_business/{{fileBasenameNoExtension}}',
)

model_args = dict(
    model_name_or_path='/mnt/lustre/share_data/chenkeqin/llava_flickr/flickr_5_99999'
)
