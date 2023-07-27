from typing import Dict
from typing import Optional

from .base import BaseDefine
from .schema import OpenApiMediaType


class OpenApiRequestBody(BaseDefine):
    _serializable = {'content', 'description', 'required'}

    content: Dict[str, OpenApiMediaType]
    description: Optional[str]
    required: Optional[bool] = False

    def __init__(self, content: Dict[str, OpenApiMediaType], **kwargs):
        """
        init
        Args:
            content: Dict[str, OpenApiMediaType]
            **kwargs:
                description: str
                required: bool
        """
        self.content = content
        super().__init__(**kwargs)
