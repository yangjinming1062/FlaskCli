from typing import Any
from typing import Optional

from .base import BaseDefine


class OpenApiExample(BaseDefine):
    _serializable = {'summary', 'description', 'value', 'externalValue'}

    summary: Optional[str]
    description: Optional[str]
    value: Optional[Any]
    externalValue: Optional[str]

    def __init__(self, **kwargs):
        """
        init
        Args:
            **kwargs:
                summary: str
                description: str
                value: Any
                externalValue: str
        """
        super().__init__(**kwargs)
