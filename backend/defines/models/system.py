"""
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
File Name   : system.py
Author      : jinming.yang
Description : 系统配置信息的定义
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
"""
from ipaddress import IPv4Address

from .base import *


class ApiRequestLogs(OLAPModelBase):
    """
    接口请求记录
    """
    __tablename__ = 'api_request_logs'
    user_id: Mapped[str_id]
    created_at: Mapped[datetime]
    method: Mapped[str_s]
    blueprint: Mapped[str_s]
    uri: Mapped[str_l]
    status: Mapped[int]
    duration: Mapped[int]
    source_ip: Mapped[IPv4Address] = mapped_column(String(16))
