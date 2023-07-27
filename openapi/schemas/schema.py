from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

from .base import BaseDefine
from .base import OpenApiSpecExtension
from .example import OpenApiExample
from .server import OpenApiServer


class OpenApiSchema(BaseDefine):
    _serializable = set()

    def __init__(self, **kwargs):
        """
        可序列化的数据即可
        Args:
            value: Any
        """
        for key, value in kwargs.items():
            self._serializable.add(key)
            setattr(self, key, value)

    def __setattr__(self, key, value):
        self._serializable.add(key)
        super().__setattr__(key, value)


class OpenApiReference(BaseDefine):
    _translate = {'ref': '$ref'}
    _serializable = {'ref', }

    ref: str
    summary: Optional[str]
    description: Optional[str]

    def __init__(self, ref, **kwargs):
        """
        init
        Args:
            ref: str
            **kwargs:
                summary: str
                description: str
        """
        self.ref = ref
        super().__init__(**kwargs)


class OpenApiEncoding(BaseDefine, OpenApiSpecExtension):
    _serializable = {'contentType', 'headers', 'style', 'explode', 'allowReserved'}

    contentType: Optional[str]
    headers: Any
    style: Optional[str]
    explode: Optional[bool]
    allowReserved: Optional[bool]

    def __init__(self, **kwargs):
        """
        init
        Args:
            **kwargs:
                contentType: str
                headers: Dict[str, Union[OpenApiHeader, OpenApiReference]]
                style: str
                explode: bool
                allowReserved: bool
        """
        super().__init__(**kwargs)


class OpenApiMediaType(BaseDefine):
    _serializable = {'schema', 'example', 'examples', 'encoding'}

    schema: Optional[Union[OpenApiSchema, OpenApiReference]]
    example: Optional[Any]
    examples: Optional[Dict[str, Union[OpenApiExample, OpenApiReference]]]
    encoding: Optional[Dict[str, OpenApiEncoding]]

    def __init__(self, **kwargs):
        """
        init
        Args:
            **kwargs:
                schema: OpenApiSchema
                example: Any
                examples: Dict[str, Union[OpenApiExample, OpenApiReference]]
                encoding: Dict[str, OpenApiEncoding]
        """
        super().__init__(**kwargs)


class OpenApiParameter(BaseDefine):
    _translate = {'in_': 'in'}
    _serializable = {
        'name', 'in_', 'description', 'required', 'deprecated', 'allowEmptyValue', 'style',
        'explode', 'allowReserved', 'schema', 'example', 'examples', 'content',
    }

    name: str
    in_: str
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

    def __init__(self, name, in_, **kwargs):
        """
        init
        Args:
            name: str
            in_: str ["query", "header", "path" or "cookie"]
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
        self.name = name
        if in_ not in ('query', 'path', 'header', 'cookie'):
            raise ValueError('in_ must be one of query, path, header, cookie')
        self.in_ = in_
        if 'style' not in kwargs:
            if in_ in ('query', 'cookie'):
                kwargs['style'] = 'form'
            else:
                kwargs['style'] = 'simple'
        if 'explode' not in kwargs:
            if kwargs['style'] == 'form':
                kwargs['explode'] = True
            else:
                kwargs['explode'] = False
        super().__init__(**kwargs)


class OpenApiOperation(BaseDefine):
    _serializable = {
        'tags', 'summary', 'description', 'externalDocs', 'operationId', 'parameters',
        'requestBody', 'responses', 'callbacks', 'deprecated', 'security', 'servers',
    }

    tags: Optional[List[str]]
    summary: Optional[str]
    description: Optional[str]
    externalDocs: Any
    operationId: Optional[str]
    parameters: Optional[List[Union[OpenApiParameter, OpenApiReference]]]
    requestBody: Any
    responses: Any
    callbacks: Any
    deprecated: Optional[bool]
    security: Any
    servers: Optional[List[OpenApiServer]]

    def __init__(self, **kwargs):
        """
        init
        Args:
            **kwargs:
                tags: List[str]
                summary: str
                description: str
                externalDocs: OpenApiExternalDocs
                operationId: str
                parameters: List[Union[OpenApiParameter, OpenApiReference]]
                requestBody: Union[OpenApiRequestBody, OpenApiReference]
                responses: OpenApiResponses
                callbacks: Dict[str, Union[OpenApiCallback, OpenApiReference]]
                deprecated: bool
                security: List[OpenApiSecurityRequirement]
                servers: List[OpenApiServer]
        """
        if 'parameters' not in kwargs:
            self.parameters = []
        if 'responses' not in kwargs:
            self.responses = {}
        super().__init__(**kwargs)


class OpenApiPathItem(BaseDefine):
    _translate = {'ref': '$ref'}
    _serializable = {
        'ref', 'summary', 'description', 'get', 'put', 'post', 'delete',
        'options', 'head', 'patch', 'trace', 'servers', 'parameters',
    }

    ref: Optional[str]
    summary: Optional[str]
    description: Optional[str]
    get: Optional[OpenApiOperation]
    put: Optional[OpenApiOperation]
    post: Optional[OpenApiOperation]
    delete: Optional[OpenApiOperation]
    options: Optional[OpenApiOperation]
    head: Optional[OpenApiOperation]
    patch: Optional[OpenApiOperation]
    trace: Optional[OpenApiOperation]
    servers: Optional[List[OpenApiServer]]
    parameters: Optional[List[Union[OpenApiParameter, OpenApiReference]]]

    def __init__(self, **kwargs):
        """
        init
        Args:
            **kwargs:
                ref: str
                summary: str
                description: str
                get: OpenApiOperation
                put: OpenApiOperation
                post: OpenApiOperation
                delete: OpenApiOperation
                options: OpenApiOperation
                head: OpenApiOperation
                patch: OpenApiOperation
                trace: OpenApiOperation
                servers: List[OpenApiServer]
                parameters: List[Union[OpenApiParameter, OpenApiReference]]
        """
        super().__init__(**kwargs)


class OpenApiCallback(BaseDefine, OpenApiSpecExtension):

    def __init__(self, **kwargs):
        """
        init
        Args:
            **kwargs:
                {expression}: Union[OpenApiPathItem, OpenApiReference]
        """
        for key, value in kwargs.items():
            if key.startswith('x-') or isinstance(value, (OpenApiPathItem, OpenApiReference)):
                setattr(self, key, value)
            else:
                raise ValueError('value must be a OpenApiPathItem or OpenApiReference')


class OpenApiDiscriminator(BaseDefine, OpenApiSpecExtension):
    _serializable = {'propertyName', 'mapping'}

    propertyName: str
    mapping: Optional[Dict[str, str]]

    def __init__(self, propertyName, **kwargs):
        """
        init
        Args:
            propertyName: str
            **kwargs:
                mapping: Dict[str, str]
        """
        self.propertyName = propertyName
        super().__init__(**kwargs)


class OpenApiExternalDoc(BaseDefine):
    _serializable = {'url', 'description'}

    url: str
    description: Optional[str]

    def __init__(self, url, **kwargs):
        """
        init
        Args:
            url: str
            **kwargs:
                description: str
        """
        self.url = url
        super().__init__(**kwargs)


class OpenApiTag(BaseDefine):
    _serializable = {'name', 'description', 'externalDocs'}

    name: str
    description: Optional[str]
    externalDocs: Optional[OpenApiExternalDoc]

    def __init__(self, name, **kwargs):
        """
        init
        Args:
            name: str
            **kwargs:
                description: str
                externalDocs: OpenApiExternalDoc
        """
        self.name = name
        super().__init__(**kwargs)


class OpenApiLink(BaseDefine, OpenApiSpecExtension):
    _serializable = {'operationRef', 'operationId', 'parameters', 'requestBody', 'description', 'server'}

    operationRef: Optional[str]
    operationId: Optional[str]
    parameters: Optional[Dict[str, Any]]
    requestBody: Optional[Any]
    description: Optional[str]
    server: Optional[OpenApiServer]

    def __init__(self, **kwargs):
        """
        init
        Args:
            **kwargs:
                operationRef: str
                operationId: str
                parameters: Dict[str, Any]
                requestBody: Any
                description: str
                server: OpenApiServer
        """
        super().__init__(**kwargs)


class OpenApiComponent(BaseDefine, OpenApiSpecExtension):
    _serializable = {
        'schemas', 'responses', 'parameters', 'examples', 'requestBodies',
        'headers', 'securitySchemes', 'links', 'callbacks', 'pathItems',
    }

    schemas: Dict[str, OpenApiSchema]
    parameters: Dict[str, Union[OpenApiParameter, OpenApiReference]]
    examples: Dict[str, Union[OpenApiExample, OpenApiReference]]
    securitySchemes: Any
    requestBodies: Any
    responses: Any
    headers: Any
    links: Dict[str, Union[OpenApiLink, OpenApiReference]]
    callbacks: Dict[str, Union[OpenApiCallback, OpenApiReference]]
    pathItems: Dict[str, Union[OpenApiPathItem, OpenApiReference]]

    def __init__(self, **kwargs):
        """
        init
        Args:
            **kwargs:
                schemas: Dict[str, OpenApiSchema]
                responses: Dict[str, Union[OpenApiResponse, OpenApiReference]]
                parameters: Dict[str, Union[OpenApiParameter, OpenApiReference]]
                examples: Dict[str, Union[OpenApiExample, OpenApiReference]]
                requestBodies: Dict[str, Union[OpenApiRequestBody, OpenApiReference]]
                headers: Dict[str, Union[OpenApiHeader, OpenApiReference]]
                securitySchemes: Dict[str, Union[OpenApiSecurity, OpenApiReference]]
                links: Dict[str, Union[OpenApiLink, OpenApiReference]]
                callbacks: Dict[str, Union[OpenApiCallback, OpenApiReference]]
                pathItems: Dict[str, Union[OpenApiPathItem, OpenApiReference]]
        """
        super().__init__(**kwargs)
