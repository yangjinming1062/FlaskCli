"""
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
File Name   : crud.py
Author      : jinming.yang@qingteng.cn
Description : 泛化CRUD接口
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
"""
from flask import Blueprint

from models import *
from utils.api import *
from . import version

bp = Blueprint('crud', __name__, url_prefix=f'/api/{version}/crud')
# 可以进行泛化操作的model及可以其包含的列
LEGAL_MODELS = {key: value.get_columns() for key, value in TPModelsDict.items()}


def target_verify_wrapper(func):
    """
    泛化接口的统一装饰器
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'target' not in kwargs:
            return response(ResponseEnum.NotFound)
        if kwargs['target'] in LEGAL_MODELS:
            return func(*args, **kwargs)
        else:
            return response(ResponseEnum.InvalidInput, LEGAL_MODELS, msg='合法的类型请参考data返回值')

    return wrapper


@bp.route('/<target>', methods=['POST'])
@api_wrapper(requires=set())
@target_verify_wrapper
def post_target(target, **kwargs):
    """
    泛化创建单一资源
    """
    return orm_create(TPModelsDict[target], kwargs['params'])


@bp.route('/<target>', methods=['GET'])
@api_wrapper(requires=set())
@target_verify_wrapper
def get_target_list(target, **kwargs):
    """
    泛化资源列表
    """
    fields = kwargs['params'].get('field')
    if fields is not None and not isinstance(fields, list):
        # 避免只查一列参数类型错误
        fields = [fields]
    return response(ResponseEnum.OK, paginate_query(TPModelsDict[target], fields))


@bp.route('/<target>/<target_id>', methods=['GET'])
@api_wrapper(requires=set())
@target_verify_wrapper
def get_target(target, target_id, **kwargs):
    """
    泛化查询单一资源
    """
    fields = kwargs['params'].get('field')
    if fields is not None and not isinstance(fields, list):
        # 避免只查一列参数类型错误
        fields = [fields]
    return orm_query(TPModelsDict[target], target_id, fields)


@bp.route('/<target>/<target_id>', methods=['PATCH'])
@api_wrapper(requires=set())
@target_verify_wrapper
def patch_target(target, target_id, **kwargs):
    """
    泛化修改单一资源
    """
    return orm_update(TPModelsDict[target], target_id, kwargs['params'])


@bp.route('/<target>', methods=['DELETE'])
@api_wrapper(requires=set('target_id'))
@target_verify_wrapper
def delete_target(target, **kwargs):
    """
    泛化删除资源
    """
    return orm_delete(TPModelsDict[target], kwargs['params']['target_id'])
