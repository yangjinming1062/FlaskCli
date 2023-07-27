from typing import Dict
from typing import List
from typing import Optional

from .base import BaseDefine


class OpenApiServerVariable(BaseDefine):
    _serializable = {'enum', 'default', 'description'}

    default: str
    enum: Optional[List[str]]
    description: Optional[str]

    def __init__(self, default: str, **kwargs):
        """
        init
        Args:
            default: str
            **kwargs:
                enum: List[str]
                description: str
        """
        self.default = default
        super().__init__(**kwargs)


class OpenApiServer(BaseDefine):
    _serializable = {'url', 'description', 'variables'}

    url: str
    description: Optional[str]
    variables: Optional[Dict[str, OpenApiServerVariable]]

    def __init__(self, url: str, **kwargs):
        """
        init
        Args:
            url: str
            **kwargs:
                description: str
                variables: Dict[str, OpenApiServerVariable]
        """
        self.url = url
        super().__init__(**kwargs)
