training_args = dict(
    # run
    output_dir=None,  # required. must be filled by derived configs.
    overwrite_output_dir=False,
    report_to='none',
    seed=42,

    # datasets
    remove_unused_columns=False,

    # train
    do_train=True,
    per_device_train_batch_size=8,
    gradient_accumulation_steps=1,
    num_train_epochs=5,
    learning_rate=2e-5,
    lr_scheduler_type='cosine',
    weight_decay=0.,
    warmup_ratio=0.03,
    evaluation_strategy='no',

    # train ddp
    tf32=True,
    bf16=True,
    gradient_checkpointing=True,
    fsdp="full_shard auto_wrap",
    fsdp_transformer_layer_cls_to_wrap='LlamaDecoderLayer',

    # train logging
    logging_steps=10,
    save_strategy='steps',
    save_steps=1000,
    save_total_limit=1,
)
