from enum import Enum


class RoleEnum(Enum):
    """
    合规枚举
    """
    Admin = '超级管理员'
    User = '用户'


class LanguageEnum(Enum):
    """
    语言枚举
    """
    ZH = 'zh-CN'
    EN = 'en-US'


class MethodEnum(Enum):
    """
    请求方法枚举
    """
    GET = 'GET'
    POST = 'POST'
    PUT = 'PUT'
    PATCH = 'PATCH'
    DELETE = 'DELETE'
