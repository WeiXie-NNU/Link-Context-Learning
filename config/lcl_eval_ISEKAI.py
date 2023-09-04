_base_ = ['_base_/dataset/DEFAULT_TEST_ISEKAI.py', '_base_/model/lcl_7b.py', '_base_/train/eval.py']

training_args = dict(
    output_dir='/mnt/lustre/share_data/chenkeqin/dummy_eval_exp_unify_mllm/{{fileBasenameNoExtension}}',

    do_train=False,
    do_eval=False,
    do_predict=False,
    do_multi_predict=True,

    fp16=True,
    fp16_full_eval=True,
    bf16=False,
    bf16_full_eval=False,
    per_device_eval_batch_size=8,
)

model_args = dict(
    model_name_or_path=None,
)

data_args = dict(
    train=None,
    validation=None,
    test=None,
    multitest=dict(
        ISEKAI_10 = dict(
            cfg = {{_base_.ISEKAI_10}}, 
            compute_metric = dict(type='ISEKAIMetrics', filename=r'/mnt/lustre/share_data/taiyan/dataset/isekai/ISEKAI-10.json')
            ),
        ISEKAI_PAIR = dict(
            cfg = {{_base_.ISEKAI_PAIR}},
            compute_metric = dict(type='ISEKAIMetrics', filename=r'/mnt/lustre/share_data/taiyan/dataset/isekai/ISEKAI-pair.json')
        )
    ),
    compute_metric=None,

    # padding collator kwargs
    collator_kwargs=dict(
        padding=True,
        max_length=1024,
    ),

    # generate config
    gen_kwargs=dict(
        max_new_tokens=1024,
        num_beams=1,
    ),
)
