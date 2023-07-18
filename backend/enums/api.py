"""
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
File Name   : api.py
Author      : jinming.yang
Description : 接口响应枚举定义
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
"""
from enum import Enum


class RespEnum(Enum):
    """
    统一接口响应枚举
    """
    # 成功
    OK = 200, {
        'code': 'OK',
        'message': '请求成功'
    }
    Created = 201, {
        'code': 'Created',
        'message': '创建成功'
    }
    NoContent = 204, {
        'code': 'NoContent',
        'message': '请求成功'
    }
    # 400错误
    BadRequest = 400, {
        'code': 'BadRequest',
        'message': '请求无效'
    }
    # 401错误
    UnAuthorized = 401, {
        'code': 'UnAuthorized',
        'message': '认证失效'
    }
    # 403错误
    Forbidden = 403, {
        'code': 'Forbidden',
        'message': '未授权进行该操作'
    }
    InUsed = 403, {
        'code': 'InUsed',
        'message': '资源使用中'
    }
    ActionRunning = 403, {
        'code': 'ActionRunning',
        'message': '同类任务正在运行中'
    }
    UnRegistered = 403, {
        'code': 'UnRegistered',
        'message': '该账号未注册'
    }
    WrongCaptcha = 403, {
        'code': 'WrongCaptcha',
        'message': '验证码失效或不正确'
    }
    WrongPassword = 403, {
        'code': 'WrongPassword',
        'message': '用户名或密码错误'
    }
    # 404错误
    NotFound = 404, {
        'code': 'NotFound',
        'message': '未找到对应资源'
    }
    UriNotFound = 404, {
        'code': 'UriNotFound',
        'message': '请求地址错误'
    }
    MethodNotFound = 404, {
        'code': 'MethodNotFound',
        'message': '请求方法错误'
    }
    # 422错误
    InvalidInput = 422, {
        'code': 'InvalidInput',
        'message': '无效输入'
    }
    KeyRepeat = 422, {
        'code': 'KeyRepeat',
        'message': '名称重复'
    }
    ParamsMissed = 422, {
        'code': 'ParamsMissed',
        'message': '缺少必填参数'
    }
    ParamsValueError = 422, {
        'code': 'ParamsValueError',
        'message': '参数类型错误'
    }
    ParamsRangeError = 422, {
        'code': 'ParamsRangeError',
        'message': '参数范围错误'
    }
    IllegalParams = 422, {
        'code': 'IllegalParams',
        'message': '非法参数/不支持的参数'
    }
    IllegalOrderField = 422, {
        'code': 'IllegalOrderField',
        'message': '无效的排序列'
    }
    IllegalOrderParams = 422, {
        'code': 'IllegalOrderParams',
        'message': '以+/-开头进行排序'
    }
    # 异常
    Error = 500, {
        'code': 'Error',
        'message': '服务端响应失败'
    }
    DBError = 500, {
        'code': 'DBError',
        'message': '数据库错误'
    }
