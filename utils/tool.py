from datetime import datetime
from functools import wraps

from utils import logger


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


def exceptions(flag_text: str = None, default=None):
    """
    装饰器：异常捕获
    :param flag_text: 自定义的附加文本
    :param default: [any]当发生异常时返回的内容，默认为None
    :return:[any]无异常则返回方法的返回值，异常返回exception_return
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kw):
            try:
                return func(*args, **kw)
            except Exception as ex:
                logger.exception(ex, func=func.__name__, plugin=flag_text)
                return default

        return wrapper

    return decorator


@exceptions()
def time_parser(timestamp, utc=False):
    """
    将时间戳转换为datetime
    :param timestamp: 请求参数中的字符串类型整秒时间戳
    :param utc: 返回UTC时间
    :return: datetime
    """
    if isinstance(timestamp, datetime):
        return timestamp
    try:
        return datetime.fromisoformat(timestamp)
    except:
        if timestamp:
            timestamp = float(str(timestamp)[:10] or 0)  # 防止传入None时报异常
            return datetime.utcfromtimestamp(timestamp) if utc else datetime.fromtimestamp(timestamp)
        return datetime.now()


def is_simple_data(for_check) -> bool:
    """
    一些内置的数据类型没有 __dict__ 和 __slots__ 属性
    :param for_check:[any]待检查的对象
    """
    return not hasattr(for_check, '__dict__') and not hasattr(for_check, '__slots__')


@exceptions()
def to_dict(obj):
    """
    类对象转成字典
    :param obj: [obj]待转换类对象，自定义数据类型
    :return: [any]内置数据类型
    """
    if obj:
        if isinstance(obj, list):
            return [to_dict(item) for item in obj]
        elif isinstance(obj, dict):
            return obj  # 如果已经是基础的字典机构了就不用再转换了
            # return {k: to_dict(v) for k, v in obj.items()}
        elif is_simple_data(obj):
            return obj
        else:
            if hasattr(obj, '__slots__'):
                return {name: to_dict(getattr(obj, name, None)) for name in obj.__slots__}
            elif hasattr(obj, '__dict__'):
                return {name: to_dict(getattr(obj, name, None)) for name in obj.__dict__}


@exceptions()
def to_obj(js_obj):
    """
    将json序列化为对象
    :param js_obj: [any]json反序列化回来的list或者dict等基础数据类型
    :return: obj:[obj]根据json内容动态决定属性内容的类对象
    """

    class CustomObject:
        def get(self, name, default=None):
            return getattr(self, name, default)

    if js_obj is None:
        return None
    elif isinstance(js_obj, list):
        result = [to_obj(x) for x in js_obj]
    elif isinstance(js_obj, dict):
        result = CustomObject()
        for key in js_obj.keys():
            setattr(result, key, to_obj(js_obj[key]))
    else:
        return js_obj
    return result
