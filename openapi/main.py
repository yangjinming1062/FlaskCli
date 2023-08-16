from datetime import datetime
from enum import EnumMeta

from sqlalchemy import Boolean
from sqlalchemy import DateTime
from sqlalchemy import Enum
from sqlalchemy import Float
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import ColumnProperty
from sqlalchemy.orm import Relationship

from apis.api import ParamDefine
from backend.main import app
from models import ModelTemplate
from models import OLAPModelsDict
from models import OLTPModelsDict
from schemas import *

# 忽略的请求类型
_MISSED_METHOD = {'OPTIONS', 'HEAD'}
# 参数url上的方法
_PARAMS_METHOD = {'GET', 'DELETE'}


def get_apispec(data, info: OpenApiInfo) -> OpenApiDefine:
    """
    生成OpenAPI定义类
    Args:
        data: 序列化方法接收的原始数据
        info: 文档信息

    Returns:
        OpenApiDefine
    """
    # 根据数据的不同选择不同的处理方式
    if isinstance(data, list):
        function = _from_data
    else:
        function = _from_app
    return function(data, info)


def _model_ref(name):
    """
    返回数据模型的引用路径
    Args:
        name:

    Returns:

    """
    return f'#/components/schemas/{name}'


def _from_app(app, info):
    """
    根据Flask应用生成OpenAPI
    Args:
        app: Flask应用
        info: OpenApiInfo

    Returns:
        OpenApiDefine
    """

    def _filed_type(field):
        """
        将ORM定义的列转换成openapi的列定义
        """
        if isinstance(field, Integer):
            return {'type': 'integer'}
        if isinstance(field, Enum):
            return {'type': 'string', 'enum': field.enums}
        if isinstance(field, String):
            return {'type': 'string'}
        if isinstance(field, Float):
            return {'type': 'number'}
        if isinstance(field, Boolean):
            return {'type': 'boolean'}
        if isinstance(field, DateTime):
            return {'type': 'string', 'format': 'date-time'}
        # JSON等特殊的一律按字符串处理
        return {'type': 'string'}

    def _parser_path(original_path: str):
        """
        将flask的接口定义转化成openapi的接口路径定义
        """
        return original_path.replace('<', '{').replace('>', '}')

    def _get_schema(param):
        """
        将参数定义转换成openapi的参数
        """
        # 1.先判断传进来的是ParamDefine还是直接的类型
        t = param.type if isinstance(param, ParamDefine) else param
        # 2.类型判断
        if str(t).startswith('typing.List'):
            l_type = t.__args__[0]
            tmp = OpenApiSchema(type='array', items=_get_schema(l_type))
        elif isinstance(t, dict):
            tmp = OpenApiSchema(type='object', properties={}, required=[])
            for k, v in t.items():
                if k.startswith('*'):
                    k = k[1:]
                    tmp.required.append(k)
                tmp.properties[k] = _get_schema(v)
        elif isinstance(t, ModelTemplate):
            tmp = OpenApiReference(_model_ref(t.__name__))
        elif issubclass(type(t), EnumMeta):
            tmp = OpenApiSchema(type='string', enum=[str(e.name) for e in list(t)], format='enum')
        elif t is datetime:
            tmp = OpenApiSchema(type='string', format='date-time')
        elif t is str:
            tmp = OpenApiSchema(type='string')
        elif t is float:
            tmp = OpenApiSchema(type='number')
        elif t is bool:
            tmp = OpenApiSchema(type='boolean')
        elif t is int:
            tmp = OpenApiSchema(type='integer')
        else:
            tmp = OpenApiSchema(type='string')
        # 3.获取注释
        if isinstance(param, ParamDefine) and param.comment:
            if isinstance(tmp, OpenApiSchema):
                tmp.title = param.comment
            else:
                tmp.description = param.comment
        return tmp

    def _get_content(data, header):
        """
        生成OpenApiRequestBody和OpenApiResponse的content
        """
        if header and 'Content-Type' in header:
            key = header['Content-Type']
        else:
            key = 'application/json'
        return {key: OpenApiMediaType(schema=_get_schema(data or {}))}

    def _get_parameters(data, in_='query'):
        """
        生成OpenApiParameter
        """
        for k, v in data.items():
            required = False
            # 1. 判断是否为必填参数
            if k.startswith('*'):
                required = True
                k = k[1:]
            param = OpenApiParameter(k, in_, required=required, schema=_get_schema(v))
            # 添加注释
            if v.comment:
                param.description = v.comment
            # 添加示例值
            if hasattr(v, 'default'):
                param.example = v.default
            yield param

    def _parser_api(endpoint_func) -> OpenApiOperation:
        """
        解析API路由函数
        Args:
            endpoint_func: 路由函数

        Returns:
            OpenApiOperation
        """
        operation = OpenApiOperation(tags=[tag], summary=endpoint_func.__doc__.strip())
        # 1.添加路径参数
        for path_arg in rule.arguments:
            operation.parameters.append(OpenApiParameter(path_arg, 'path', required=True))
        # 2.生成请求头参数
        if req_header := endpoint_func.__apispec__['request_header']:
            operation.parameters.extend(_get_parameters(req_header, 'header'))
        # 3. 生成请求参数
        if req_param := endpoint_func.__apispec__['request']:
            # 3.1 生成params参数
            if method in _PARAMS_METHOD:
                operation.parameters.extend(_get_parameters(req_param))
            # 3.2 生成请求体参数
            else:
                operation.requestBody = OpenApiRequestBody(_get_content(req_param, req_header))
        # 4.生成响应参数
        for resp, data in endpoint_func.__apispec__['response'].items():
            code, msg = resp.value
            body = {
                'code': resp.name,
                'message': msg
            }
            content = _get_content(data, endpoint_func.__apispec__['response_header'])
            operation.responses[str(code)] = OpenApiResponse(body, content=content)
        return operation

    # ***从这开始from_app的代码***
    apispec = OpenApiDefine(info, paths={})
    # 1.根据蓝图定义指定tags
    apispec.tags = [OpenApiTag(bp.name) for bp in app.blueprints.values()]
    # 2. 根据model定义生成schema定义
    schemas = {}
    # 2.1 这里把OLAP、OLTP的定义都进行了导出，按需调整
    for model_dict in (OLAPModelsDict, OLTPModelsDict):
        for name, model in model_dict.items():
            properties = {}
            for prop in model.__mapper__.iterate_properties:
                if isinstance(prop, ColumnProperty):
                    prop = prop.columns[0]
                    properties[prop.key] = _filed_type(prop.type)
                    if getattr(prop, 'comment', None):
                        properties[prop.key]['title'] = prop.comment
                elif isinstance(prop, Relationship):
                    ref = OpenApiReference(_model_ref(prop.argument))
                    if prop.uselist:
                        properties[prop.key] = {'type': 'array', 'items': ref}
                    else:
                        properties[prop.key] = ref
            schemas[name] = OpenApiSchema(type='object', properties=properties, title=model.__doc__.strip())
    apispec.components = OpenApiComponent(schemas=schemas)
    # 3.生成接口定义
    endpoint_dict = {e: f for e, f in app.view_functions.items() if getattr(f, '__apispec__', None)}
    for rule in app.url_map.iter_rules():
        if rule.endpoint in endpoint_dict:
            path = apispec.paths.setdefault(_parser_path(rule.rule), OpenApiPathItem())
            method = list(rule.methods - _MISSED_METHOD)[0]
            tag = rule.endpoint.split('.')[0]
            setattr(path, method.lower(), _parser_api(endpoint_dict[rule.endpoint]))
    return apispec


def _from_data(data, info):
    """
    通过指定API定义数据生成接口文档
    Args:
        data: API定义列表
        info: OpenApiInfo

    Returns:
        OpenApiDefine
    """
    result = OpenApiDefine(info)
    # TODO
    return result


if __name__ == '__main__':
    api = get_apispec(app, OpenApiInfo('flaskcli', 'mvp'))
    doc = api.to_file('schema.json')
