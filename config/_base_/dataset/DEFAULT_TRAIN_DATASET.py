_base_ = [
    'DEFAULT_TRAIN_GQA_VARIANT.py',
    'DEFAULT_TRAIN_CLEVR_VARIANT.py',
    'DEFAULT_TRAIN_POINT_VARIANT.py',
    'DEFAULT_TRAIN_GPTGEN_VARIANT.py',
    'DEFAULT_TRAIN_VCR_VARIANT.py',
    'DEFAULT_TRAIN_VQAv2_VARIANT.py',
    'DEFAULT_TRAIN_VQAEX_VARIANT.py',
    'DEFAULT_TRAIN_V3DET_VARIANT.py',
    'DEFAULT_TRAIN_IMAGENET.py',
]

DEFAULT_TRAIN_DATASET = dict(
    flickr=dict(
        type='FlickrDataset',
        filename=r'/mnt/lustre/share_data/chenkeqin/mllm_data/pretrain_data/ann/CWB_flickr30k_train.jsonl',
        image_folder=r'zz1424:s3://production-public-flickr_image/Flickr_Image/unzip/flickr30k_images/flickr30k_images',
        template_file=r'{{fileDirname}}/template/flickr30k.json',
    ),
    rec=dict(
        type='RECDataset',
        filename=r'/mnt/lustre/share_data/chenkeqin/mllm_data/pretrain_data/ann/REC_ref3_train.jsonl',
        template_file=r'{{fileDirname}}/template/REC.json',
    ),
    recvg=dict(
        type='RECDataset',
        filename=r'/mnt/lustre/share_data/chenkeqin/mllm_data/pretrain_data/ann/GC_genome196_train.jsonl',
        template_file=r'{{fileDirname}}/template/REC.json',
    ),
    reg=dict(
        type='REGDataset',
        filename=r'/mnt/lustre/share_data/chenkeqin/mllm_data/pretrain_data/ann/REC_ref3_train.jsonl',
        template_file=r'{{fileDirname}}/template/REG.json',
    ),
    gc=dict(
        type='GCDataset',
        filename=r'/mnt/lustre/share_data/chenkeqin/mllm_data/pretrain_data/ann/GC_genome196_train.jsonl',
        template_file=r'{{fileDirname}}/template/GC.json',
    ),
    caption=dict(
        type='CaptionDataset',
        filename=r'/mnt/lustre/share_data/chenkeqin/mllm_data/pretrain_data/ann/CAP_coco2014_train.jsonl',
        template_file=r'{{fileDirname}}/template/image_cap.json',
    ),
    llavacc3m=dict(
        type='InstructDataset',
        filename=r"/mnt/lustre/share_data/chenkeqin/mllm_data/pretrain_data/ann/llava_cc3m.jsonl",
        image_folder=r'sh41:s3://MultiModal/Monolith/academic/llava-pretrain/data/558K_imgs',   # TODO: zz make folder name mistake
    ),
    llavalcs=dict(
        type='InstructDataset',
        filename=r"/mnt/lustre/share_data/chenkeqin/mllm_data/pretrain_data/ann/blip_laion_cc_sbu_558k.jsonl",
        image_folder=r'sh41:s3://MultiModal/Monolith/academic/llava-pretrain/data/595K_imgs',   # TODO: zz make folder name mistake
    ),
    instruct=dict(
        type='InstructDataset',
        filename=r'/mnt/lustre/share_data/chenkeqin/mllm_data/pretrain_data/ann/llava_instruct_150k.jsonl',
        image_folder=r'zz1424:s3://PublicDatalist/public_datalist_6_unzip/train2014',
        add_coco_prefix=True,
    ),
    v3det=dict(
        type='V3DetDataset',
        filename=r'/mnt/lustre/share_data/zhangzhao2/VG/v3det/v3det_2023_v1_train_neig_expired.json',
        image_folder=r'sdc:s3://mm_data/v3det/',
        template_file=r"{{fileDirname}}/template/ICL.json",
    ),
    imagenet_v13_update=dict(
        type='ImageNet1kDatasetTrain',
        filename=r'/mnt/lustre/share_data/taiyan/dataset/imagenet1k/train900_pairs.jsonl',
        image_folder=r'ty1424:s3://production-public-imagenet/ImageNet/unzip/ILSVRC/Data/CLS-LOC/',
        template_file=r"{{fileDirname}}/template/ICL.json",
        policy="policy_v13_update",
    ),
    imagenet_jigsaw_v1=dict(
        type='ImageNet1kDatasetTrain',
        filename=r'/mnt/lustre/share_data/taiyan/dataset/imagenet1k/train900_pairs.jsonl',
        image_folder=r'ty1424:s3://production-public-imagenet/ImageNet/unzip/ILSVRC/Data/CLS-LOC/',
        template_file=r"{{fileDirname}}/template/ICL.json",
        policy="policy_jigsaw",
    ),
    **_base_.DEFAULT_TRAIN_GQA_VARIANT,
    **_base_.DEFAULT_TRAIN_CLEVR_VARIANT,
    **_base_.DEFAULT_TRAIN_POINT_VARIANT,
    **_base_.DEFAULT_TRAIN_GPTGEN_VARIANT,
    **_base_.DEFAULT_TRAIN_VCR_VARIANT,
    **_base_.DEFAULT_TRAIN_VQAv2_VARIANT,
    **_base_.DEFAULT_TRAIN_VQAEX_VARIANT,
    **_base_.DEFAULT_TRAIN_V3DET_VARIANT,
    **_base_.IMAGENET1K_TRAIN,
)
