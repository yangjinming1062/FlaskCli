from typing import Optional

from .base import BaseDefine


class OpenApiContact(BaseDefine):
    _serializable = {'name', 'url', 'email'}

    name: Optional[str]
    url: Optional[str]
    email: Optional[str]

    def __init__(self, **kwargs):
        """
        init
        Args:
            **kwargs:
                name: str
                url: str
                email: str
        """
        super().__init__(**kwargs)


class OpenApiLicense(BaseDefine):
    _serializable = {'name', 'identifier', 'url'}

    name: str
    identifier: Optional[str]
    url: Optional[str]

    def __init__(self, name: str, **kwargs):
        """
        init
        Args:
            name: str
            **kwargs:
                identifier: str
                url: str
        """
        self.name = name
        super().__init__(**kwargs)


class OpenApiInfo(BaseDefine):
    _serializable = {'title', 'version', 'summary', 'description', 'termsOfService', 'contact', 'license'}

    title: str
    version: str
    summary: Optional[str]
    description: Optional[str]
    termsOfService: Optional[str]
    contact: Optional[OpenApiContact]
    license: Optional[OpenApiLicense]

    def __init__(self, title: str, version: str, **kwargs):
        """
        init
        Args:
            title: str
            version: str
            **kwargs:
                summary: str
                description: str
                termsOfService: str
                contact: OpenApiContact
                license: OpenApiLicense
        """
        self.title = title
        self.version = version
        super().__init__(**kwargs)
