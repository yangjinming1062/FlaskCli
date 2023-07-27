from typing import Dict
from typing import Optional
from typing import Union

from .base import BaseDefine
from .header import OpenApiHeader
from .schema import OpenApiLink
from .schema import OpenApiMediaType
from .schema import OpenApiReference


class OpenApiResponse(BaseDefine):
    _serializable = {'description', 'headers', 'content', 'links'}

    description: str
    headers: Optional[Dict[str, Union[OpenApiHeader, OpenApiReference]]]
    content: Optional[Dict[str, OpenApiMediaType]]
    links: Optional[Dict[str, Union[OpenApiLink, OpenApiReference]]]

    def __init__(self, description, **kwargs):
        """
        init
        Args:
            description: str
            **kwargs:
                headers: Dict[str, Union[OpenApiHeader, OpenApiReference]]
                content: Dict[str, OpenApiMediaType]
                links: Dict[str, str]
        """
        self.description = description
        super().__init__(**kwargs)
