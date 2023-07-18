"""
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
File Name   : __init__.py
Author      : jinming.yang
Description : 定义使用的蓝图及鉴权规则
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
"""
import os
import re
from glob import glob

from flask import Blueprint

for name in glob(os.path.dirname(__file__) + '/v*/*.??'):
    if os.path.isfile(name) and not name.endswith('__.py'):
        api, version, name = name[:-3].split(os.sep)
        expression = f'from {api}.{version}.{name} import bp as {name}_{version}_bp'
        exec(expression)

# Blueprints用于在创建app时动态注册蓝图
Blueprints = [module for name, module in globals().items() if name.endswith('_bp') and isinstance(module, Blueprint)]

# 无需进行鉴权的接口的正则表达式
SKIP_AUTH_REGEX = re.compile(r'^/api/v1/auth|^/api/v1/common')
