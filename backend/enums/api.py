from enum import Enum


class RespEnum(Enum):
    """
    统一接口响应枚举
    """
    # 成功
    OK = 200, '请求成功'
    Created = 201, '创建成功'
    Accepted = 202, '任务运行中'
    NoContent = 204, '请求成功'
    # 400错误
    BadRequest = 400, '请求无效'
    # 401错误
    UnAuthorized = 401, '认证失效'
    # 403错误
    Forbidden = 403, '未授权进行该操作'
    InUsed = 403, '资源使用中'
    UnRegistered = 403, '该账号未注册'
    WrongCaptcha = 403, '验证码错误'
    WrongPassword = 403, '用户名或密码错误'
    # 404错误
    NotFound = 404, '未找到对应资源'
    UriNotFound = 404, '请求地址错误'
    MethodNotFound = 404, '请求方法错误'
    # 422错误
    InvalidInput = 422, '无效输入'
    KeyRepeat = 422, '关键字重复'
    ParamsMissed = 422, '缺少必填参数'
    ParamsValueError = 422, '参数类型错误'
    ParamsRangeError = 422, '参数范围错误'
    IllegalParams = 422, '不支持的参数'
    IllegalOrderField = 422, '无效的排序列'
    IllegalOrderParams = 422, '以+/-开头进行排序'
    InvalidAccount = 422, '无效账号'
    InvalidUsername = 422, '无效用户名'
    InvalidPassword = 422, '无效密码'
    InvalidPhone = 422, '无效手机号'
    InvalidEmail = 422, '无效邮箱'
    InvalidKey = 422, '无效的访问密钥'
    # 异常
    Error = 500, '服务端响应失败'
    DBError = 500, '数据库错误'
