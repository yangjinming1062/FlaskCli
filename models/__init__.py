"""
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
File Name   : __init__.py
Author      : jinming.yang
Description : 在__init__.py中统一导入
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
"""
from .base import APModelBase
from .base import TPModelBase
from .base import ap_engine
from .base import ap_public_session
from .base import tp_engine
from .base import tp_public_session
from .business import *
from .system import *

APModelsDict = {}  # 全部的OLAP模型定义
TPModelsDict = {}  # 全部的OLTP模型定义

_base = [
    'APModelBase',
    'TPModelBase',
    'ap_engine',
    'tp_engine',
    'ap_public_session',
    'tp_public_session',
    'APModelsDict',
    'TPModelsDict',
]
_G = {n: m for n, m in locals().items() if isinstance(m, type)}
for name, module in _G.items():
    if issubclass(module, APModelBase) and name != 'APModelBase':
        APModelsDict[name] = module
    elif issubclass(module, TPModelBase) and name != 'TPModelBase':
        TPModelsDict[name] = module

# 限制 from models import * 时导入的内容
__all__ = _base + list(APModelsDict.keys()) + list(TPModelsDict.keys())
