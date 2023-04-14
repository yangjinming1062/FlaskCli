"""
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
File Name   : __init__.py
Author      : jinming.yang
Description : 定义使用的蓝图及鉴权规则
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
"""
import re

from flask import Blueprint

# 只需要在这里导入需要的bp即可自动添加到app中
from apis.v1.auth import bp as auth_v1_bp
from apis.v1.chart import bp as chart_v1_bp
from apis.v1.crud import bp as crud_v1_bp
from apis.v1.function import bp as function_v1_bp

# Blueprints用于在创建app时动态注册蓝图
Blueprints = [module for name, module in globals().items() if name.endswith('_bp') and isinstance(module, Blueprint)]

# 无需进行鉴权的接口的正则表达式
SKIP_AUTH_REGEX = re.compile(r'^/api/v1/auth|^/api/v1/common')
