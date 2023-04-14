"""
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
File Name   : response.py
Author      : jinming.yang
Description : 接口响应枚举定义
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
"""
from enum import Enum


class ResponseEnum(Enum):
    """
    统一接口响应枚举，统一接口的返回信息（响应）格式
    元组分别是：响应状态码，响应状态，默认消息
    """
    OK = 200, 'Success', '请求成功'

    Created = 201, 'Success', '创建成功'

    NoContent = 204, 'No Content', '请求成功'

    BadRequest = 400, 'Bad Request', '请求无效'

    UnAuthorized = 401, 'Authorized Invalid', '认证失效'

    Forbidden = 403, 'Forbidden', '未授权进行该操作'

    NotFound = 404, 'Not Found', '未找到对应资源'

    InvalidInput = 422, 'Invalid Input', '无效输入'

    MissingParams = 422, 'Missing Parameter', '缺少必填参数'

    Error = 500, 'Server Error', '服务端响应失败'
