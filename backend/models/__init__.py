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
from .business import User
from .system import ApiRequestLogs

_base = [
    'OLAPEngine',
    'OLAPModelBase',
    'OLAPModelsDict',
    'OLTPEngine',
    'OLTPModelBase',
    'OLTPModelsDict',
    'ModelTemplate'
]

OLAPModelsDict = {n: m for n, m in locals().items() if isinstance(m, type) and issubclass(m, OLAPModelBase)}
OLAPModelsDict.pop('OLAPModelBase', None)

OLTPModelsDict = {n: m for n, m in locals().items() if isinstance(m, type) and issubclass(m, OLTPModelBase)}
OLTPModelsDict.pop('OLTPModelBase', None)

# 限制 from models import * 时导入的内容
__all__ = _base + list(OLAPModelsDict.keys()) + list(OLTPModelsDict.keys())
