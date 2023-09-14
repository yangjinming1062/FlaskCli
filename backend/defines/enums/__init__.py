"""
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
File Name   : __init__.py
Author      : jinming.yang
Description : 在__init__.py中统一导入
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
"""
from enum import Enum

# from .system import *

_base = ['Enum', ]
_enums = [name for name, module in locals().items() if name.endswith('Enum') and issubclass(module, Enum)]
# 限制 from enums import * 时导入的内容
__all__ = _base + _enums
