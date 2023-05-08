"""
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
File Name   : __init__.py
Author      : jinming.yang
Description : 在__init__.py中统一导入
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
"""
from .base import ModelTemplate
from .base import OLAPModelBase
from .base import OLTPModelBase
from .business import *
from .system import *

OLAPModelsDict = {}  # 全部的OLAP模型定义
OLTPModelsDict = {}  # 全部的OLTP模型定义

_base = [
    'OLAPModelBase',
    'OLTPModelBase',
    'ModelTemplate',
    'OLAPModelsDict',
    'OLTPModelsDict',
]
_G = {n: m for n, m in locals().items() if isinstance(m, type)}
for name, module in _G.items():
    if issubclass(module, OLAPModelBase) and name != 'OLAPModelBase':
        OLAPModelsDict[name] = module
    elif issubclass(module, OLTPModelBase) and name != 'OLTPModelBase':
        OLTPModelsDict[name] = module

# 限制 from models import * 时导入的内容
__all__ = _base + list(OLAPModelsDict.keys()) + list(OLTPModelsDict.keys())
