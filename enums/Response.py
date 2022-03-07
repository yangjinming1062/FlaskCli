from enum import Enum


class ResponseEnum(Enum):
    """
    统一接口响应枚举，统一接口的返回信息（响应）格式
    """
    SUCCESS_200 = {'code': 200, 'status': 'Success', "msg": "请求成功"}

    SUCCESS_201 = {'code': 201, 'status': 'Success', "msg": "创建成功"}

    SUCCESS_204 = {'code': 204, 'status': 'No Content', "msg": "请求成功"}

    BAD_REQUEST_400 = {"code": 400, "status": "Bad Request", "msg": "请求无效"}

    UNAUTHORIZED_401 = {"code": 401, "status": "Authorized Invalid", "msg": "认证失效"}

    FORBIDDEN_403 = {"code": 403, "status": "Not Authorized", "msg": "未授权进行该操作"}

    NOT_FOUND_404 = {"code": 404, "status": "Not Found", "msg": "未找到对应资源"}

    INVALID_INPUT_422 = {"code": 422, "status": "Invalid Input", "msg": "无效输入"}

    MISSING_PARAMETERS_422 = {"code": 422, "status": "Missing Parameter", "msg": "缺少必填参数"}

    SERVER_ERROR_500 = {"code": 500, "status": "Server Error", "msg": "服务端响应失败"}
