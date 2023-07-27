import json
from datetime import datetime
from enum import Enum
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

import pytz

from .base import BaseDefine
from .example import OpenApiExample
from .header import OpenApiHeader
from .info import OpenApiContact
from .info import OpenApiInfo
from .info import OpenApiLicense
from .request_body import OpenApiRequestBody
from .response import OpenApiResponse
from .schema import OpenApiCallback
from .schema import OpenApiComponent
from .schema import OpenApiDiscriminator
from .schema import OpenApiEncoding
from .schema import OpenApiExternalDoc
from .schema import OpenApiLink
from .schema import OpenApiMediaType
from .schema import OpenApiOperation
from .schema import OpenApiParameter
from .schema import OpenApiPathItem
from .schema import OpenApiReference
from .schema import OpenApiSchema
from .schema import OpenApiTag
from .security import OpenApiOAuthFlow
from .security import OpenApiOAuthFlows
from .security import OpenApiSecurity
from .security import OpenApiSecurityRequirement
from .server import OpenApiServer
from .server import OpenApiServerVariable

tz = pytz.timezone('Asia/Shanghai')


class ExtensionJSONEncoder(json.JSONEncoder):
    """
    处理枚举等各种无法JSON序列化的类型
    """

    def default(self, obj):
        if isinstance(obj, Enum):
            return obj.value
        if isinstance(obj, datetime):
            return obj.astimezone(tz).isoformat(timespec='seconds')
        if isinstance(obj, BaseDefine):
            return obj.json()
        return json.JSONEncoder.default(self, obj)


class OpenApiDefine(BaseDefine):
    _serializable = {
        'openapi', 'info', 'jsonSchemaDialect', 'servers', 'paths', 'components', 'security', 'tags', 'externalDocs',
    }

    openapi: str = '3.1.0'
    info: OpenApiInfo
    jsonSchemaDialect: Optional[str] = '$schema'
    servers: Optional[List[OpenApiServer]]
    paths: Optional[Dict[str, OpenApiPathItem]]
    webhooks: Optional[Dict[str, Union[OpenApiPathItem, OpenApiReference]]]
    components: Optional[OpenApiComponent]
    security: Optional[List[OpenApiSecurityRequirement]]
    tags: Optional[List[OpenApiTag]]
    externalDocs: Optional[OpenApiExternalDoc]

    def __init__(self, info: OpenApiInfo, **kwargs):
        """
        init
        Args:
            info: OpenApiInfo
            **kwargs:
                jsonSchemaDialect: str
                servers: List[OpenApiServer]
                paths: Dict[str, OpenApiPathItem]
                webhooks: Dict[str, Union[OpenApiPathItem, OpenApiReference]]
                components: OpenApiComponent
                security: List[OpenApiSecurityRequirement]
                tags: List[OpenApiTag]
                externalDocs: OpenApiExternalDoc
        """
        self.info = info
        super().__init__(**kwargs)

    def to_file(self, file_path: str):
        """
        生成文件
        Args:
            file_path: 文件路径
        """
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.json(), f, indent=4, cls=ExtensionJSONEncoder)


__all__ = [
    'OpenApiDefine',
    'OpenApiInfo',
    'OpenApiContact',
    'OpenApiLicense',
    'OpenApiServer',
    'OpenApiServerVariable',
    'OpenApiComponent',
    'OpenApiPathItem',
    'OpenApiOperation',
    'OpenApiExternalDoc',
    'OpenApiParameter',
    'OpenApiRequestBody',
    'OpenApiMediaType',
    'OpenApiEncoding',
    'OpenApiResponse',
    'OpenApiCallback',
    'OpenApiExample',
    'OpenApiLink',
    'OpenApiHeader',
    'OpenApiTag',
    'OpenApiReference',
    'OpenApiSchema',
    'OpenApiDiscriminator',
    'OpenApiSecurity',
    'OpenApiSecurityRequirement',
    'OpenApiOAuthFlows',
    'OpenApiOAuthFlow',
]
