# Copyright (c) Facebook, Inc. and its affiliates. All Rights Reserved
from fvcore.common.registry import Registry

DATASET_MAPPER_REGISTRY = Registry("DATASET_MAPPER_REGISTRY")  # noqa F401 isort:skip
DATASET_MAPPER_REGISTRY.__doc__ = """

"""


def build_dataset_mapper(cfg):
    """
    Build the whole model architecture, defined by ``cfg.MODEL.META_ARCHITECTURE``.
    Note that it does not load any weights from ``cfg``.
    """
    dataset_mapper = cfg.dataset.dataset_mapper
    return DATASET_MAPPER_REGISTRY.get(dataset_mapper)(cfg)
