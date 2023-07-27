from typing import Any
from typing import Dict
from typing import Optional
from typing import Union

from .base import BaseDefine
from .example import OpenApiExample
from .schema import OpenApiMediaType
from .schema import OpenApiReference
from .schema import OpenApiSchema


class OpenApiHeader(BaseDefine):
    _serializable = {
        'description', 'required', 'deprecated', 'allowEmptyValue', 'style',
        'explode', 'allowReserved', 'schema', 'example', 'examples', 'content'
    }

    description: Optional[str]
    required: Optional[bool] = False
    deprecated: Optional[bool] = False
    allowEmptyValue: Optional[bool]
    style: Optional[str]
    explode: Optional[bool]
    allowReserved: Optional[bool] = False
    schema: Optional[OpenApiSchema]
    example: Optional[Any]
    examples: Optional[Dict[str, Union[OpenApiExample, OpenApiReference]]]
    content: Optional[Dict[str, OpenApiMediaType]]

    def __init__(self, **kwargs):
        """
        init
        Args:
            **kwargs:
                description: str
                required: bool
                deprecated: bool
                allowEmptyValue: bool
                style: str
                explode: bool
                allowReserved: bool
                schemas: OpenApiSchema
                example: Any
                examples: Dict[str, Union[OpenApiExample, OpenApiReference]]
                content: Dict[str, OpenApiMediaType]
        """
        super().__init__(**kwargs)
