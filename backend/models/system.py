"""
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
File Name   : system.py
Author      : jinming.yang
Description : 该文件中主要用于定义一些系统配置等非用户相关的模型
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
"""
from ipaddress import IPv4Address

from .base import *


class ApiRequestLogs(OLAPModelBase, TimeColumns):
    """
    接口请求记录
    """
    __tablename__ = 'api_request_logs'
    user_id: Mapped[str_id]
    method: Mapped[str_s]
    version: Mapped[str_s]
    blueprint: Mapped[str_s]
    uri: Mapped[str_l]
    status_code: Mapped[int]
    duration: Mapped[int]
    source_ip: Mapped[IPv4Address]
    destination_ip: Mapped[IPv4Address]
