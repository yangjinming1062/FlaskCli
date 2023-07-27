from typing import Dict
from typing import List
from typing import Optional

from .base import BaseDefine
from .base import OpenApiSpecExtension


class OpenApiOAuthFlow(BaseDefine, OpenApiSpecExtension):
    _translate = {
        'authorization_url': 'authorizationUrl',
        'token_url': 'tokenUrl',
        'refresh_url': 'refreshUrl'
    }
    _serializable = {'authorization_url', 'token_url', 'scopes', 'refresh_url'}

    authorization_url: str
    token_url: str
    scopes: Dict[str, str]
    refresh_url: Optional[str]

    def __init__(self, authorization_url, token_url, scopes, **kwargs):
        """
        init
        Args:
            authorization_url: str
            token_url: str
            scopes: Dict[str, str]
            **kwargs:
                refresh_url: str
        """
        self.authorization_url = authorization_url
        self.tokenUrl = token_url
        self.scopes = scopes
        super().__init__(**kwargs)


class OpenApiOAuthFlows(BaseDefine):
    _translate = {
        'client_credentials': 'clientCredentials',
        'authorization_code': 'authorizationCode',
    }
    _serializable = {'implicit', 'password', 'client_credentials', 'authorization_code'}

    implicit: Optional[OpenApiOAuthFlow]
    password: Optional[OpenApiOAuthFlow]
    client_credentials: Optional[OpenApiOAuthFlow]
    authorization_code: Optional[OpenApiOAuthFlow]

    def __init__(self, **kwargs):
        """
        init
        Args:
            **kwargs:
                implicit: OpenApiOAuthFlow
                password: OpenApiOAuthFlow
                client_credentials: OpenApiOAuthFlow
                authorization_code: OpenApiOAuthFlow
        """
        super().__init__(**kwargs)


class OpenApiSecurity(BaseDefine, OpenApiSpecExtension):
    _translate = {'type_': 'type', 'in_': 'in', 'open_id_connect_url': 'openIdConnectUrl'}
    _serializable = ('type_', 'in_', 'name', 'scheme', 'description', 'bearerFormat', 'flows', 'open_id_connect_url')

    type_: str
    in_: str
    name: str
    scheme: str
    open_id_connect_url: str
    flows: OpenApiOAuthFlows
    description: Optional[str]
    bearerFormat: Optional[str]

    def __init__(self, type_, in_, name, scheme, flows, open_id_connect_url, **kwargs):
        """
        init
        Args:
            type_: ["apiKey", "http", "mutualTLS", "oauth2", "openIdConnect"]
            in_: str ["query", "header" or "cookie"]
            name: str
            scheme: str
            flows: OpenApiOAuthFlows
            open_id_connect_url: str
            **kwargs:
                description: str
                bearerFormat: str
        """
        self.type_ = type_
        self.in_ = in_
        self.name = name
        self.scheme = scheme
        self.flows = flows
        self.open_id_connect_url = open_id_connect_url
        super().__init__(**kwargs)


class OpenApiSecurityRequirement(BaseDefine):
    _serializable = set()

    def __init__(self, **kwargs):
        """
        init
        Args:
            **kwargs:
                {name}: List[str]
        """
        for key, value in kwargs.items():
            if type(value) != List[str]:
                raise TypeError(f"{key} must be a list")
            setattr(self, key, value)

    def __setattr__(self, key, value):
        self._serializable.add(key)
        super().__setattr__(key, value)
