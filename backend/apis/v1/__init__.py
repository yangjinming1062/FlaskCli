"""
这里可以定义一些接口可以共用到的Schema
"""
from typing import List

from ..common import ParamDefine
from ..common import ParamSchema


class CreatedSchema(ParamSchema):
    define = ParamDefine(str, True)


class PaginateRequestSchema(ParamSchema):
    """
    分页类请求共同参数定义
    """
    public = {
        'page': ParamDefine(int, True, '页码'),
        'size': ParamDefine(int, True, '单页数量'),
        'sort': ParamDefine(List[str], False, '排序字段'),
    }

    def __init__(self, detail: dict):
        """
        通过detail传入不同分页接口的差异部分
        Args:
            detail:
        """
        self.define = ParamDefine(self.public | detail)


class PaginateResponseSchema(ParamSchema):
    """
    分页类响应共同参数定义
    """

    def __init__(self, detail):
        """
        通过detail传入不同分页接口的差异部分
        Args:
            detail:
        """
        self.define = ParamDefine({
            'total': ParamDefine(int, True, '总数'),
            'data': ParamDefine(List[detail], True, '数据列表'),
        }, True)
