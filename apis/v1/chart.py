"""
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
File Name   : chart.py
Author      : jinming.yang
Description : 实现和报表、可视化相关的API接口
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
"""
from flask import Blueprint

from . import version

bp = Blueprint('chart', __name__, url_prefix=f'/api/{version}/chart')
