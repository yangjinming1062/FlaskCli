def serialize(obj):
    """
    类对象转成基础数据类型
    Args:
        obj: 待转换类对象，自定义数据类型

    Returns:
        序列化对象
    """
    if obj:
        if isinstance(obj, list):
            return [serialize(item) for item in obj]
        elif isinstance(obj, dict):
            return obj  # 如果已经是基础的字典机构了就不用再转换了
        elif isinstance(obj, BaseDefine):
            result = {}
            for name in obj._serializable:
                if value := getattr(obj, name, None):
                    if obj._translate and name in obj._translate:
                        name = obj._translate[name]
                    result[name] = serialize(value)
            return result
        else:
            return obj


class BaseDefine:
    _translate = None
    _serializable = None

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if key not in self._serializable:
                if issubclass(type(self), OpenApiSpecExtension) and key.startswith('x-'):
                    self._serializable.add(key)
                else:
                    raise KeyError(f'{key} is not in {self._serializable}')
            setattr(self, key, value)

    def json(self):
        return serialize(self)


class OpenApiSpecExtension:
    """
    The extensions properties are implemented as patterned fields that are always prefixed by "x-"
    """
    _serializable = set()

    def __setattr__(self, key, value):
        self._serializable.add(key)
        super().__setattr__(key, value)
