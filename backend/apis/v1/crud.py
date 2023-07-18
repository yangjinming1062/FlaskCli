"""
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
File Name   : crud.py
Author      : jinming.yang@qingteng.cn
Description : 泛化CRUD接口
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
"""
from models import *
from utils.api import *

bp = get_blueprint(__name__)
# 可以进行泛化操作的model及可以其包含的列
LEGAL_MODELS = {key: value.get_columns() for key, value in OLTPModelsDict.items()}


def target_verify_wrapper(function):
    """
    泛化接口的统一装饰器
    """

    @wraps(function)
    def wrapper(*args, **kwargs):
        if 'target' not in kwargs:
            return response(RespEnum.NotFound)
        if kwargs['target'] in LEGAL_MODELS:
            return function(*args, **kwargs)
        else:
            return response(RespEnum.ParamsRangeError, LEGAL_MODELS)

    return wrapper


@bp.route('/<target>', methods=['POST'])
@api_wrapper(params={})
@target_verify_wrapper
def post_target(target, **kwargs):
    """
    泛化创建单一资源
    """
    return orm_create(OLTPModelsDict[target], kwargs)


@bp.route('/<target>/search', methods=['POST'])
@api_wrapper(params={'*page': int, '*size': int, 'query': dict, 'sort': list, 'field': list})
@target_verify_wrapper
def search_target_list(target, **kwargs):
    """
    泛化资源列表
    """
    return response(RespEnum.OK, orm_paginate(OLTPModelsDict[target], kwargs))


@bp.route('/<target>/<target_id>', methods=['GET'])
@api_wrapper(params={})
@target_verify_wrapper
def get_target(target, target_id, **kwargs):
    """
    泛化查询单一资源
    """
    fields = kwargs.get('field')
    if fields is not None and not isinstance(fields, list):
        # 避免只查一列参数类型错误
        fields = [fields]
    return orm_read(OLTPModelsDict[target], target_id, fields)


@bp.route('/<target>/<target_id>', methods=['PATCH'])
@api_wrapper(params={})
@target_verify_wrapper
def patch_target(target, target_id, **kwargs):
    """
    泛化修改单一资源
    """
    return orm_update(OLTPModelsDict[target], target_id, kwargs)


@bp.route('/<target>', methods=['DELETE'])
@api_wrapper(params={'*id': None})
@target_verify_wrapper
def delete_target(target, **kwargs):
    """
    泛化删除资源
    """
    return orm_delete(OLTPModelsDict[target], kwargs['id'])