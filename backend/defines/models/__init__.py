"""
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
File Name   : __init__.py
Author      : jinming.yang
Description : 在__init__.py中统一导入
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
"""
from .base import ModelTemplate
from .base import OLAPEngine
from .base import OLAPModelBase
from .base import OLTPEngine
from .base import OLTPModelBase

_base = [
    'ModelTemplate',
    'OLAPEngine',
    'OLAPModelBase',
    'OLAPModelsDict',
    'OLTPEngine',
    'OLTPModelBase',
    'OLTPModelsDict',
]

OLAPModelsDict = {x.__name__: x for x in OLAPModelBase.__subclasses__()}
OLTPModelsDict = {x.__name__: x for x in OLTPModelBase.__subclasses__()}

# 限制 from models import * 时导入的内容
__all__ = _base + list(OLAPModelsDict.keys()) + list(OLTPModelsDict.keys())
