"""
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
File Name   : system.py
Author      : jinming.yang
Description : 该文件中主要用于定义一些系统配置等非用户相关的模型
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
"""
from datetime import datetime
from ipaddress import IPv4Address

from .base import *


class ApiRequestLogs(OLAPModelBase):
    """
    接口请求记录
    """
    __tablename__ = 'api_request_logs'
    user_id: Union[Column, str] = Column(types.String, comment='用户ID')
    create_time: Union[Column, datetime] = Column(types.DateTime64, comment='请求时间')
    method: Union[Column, str] = Column(types.String, comment='请求方式')
    version: Union[Column, str] = Column(types.String, comment='接口版本')
    blueprint: Union[Column, str] = Column(types.String, comment='所属模块')
    uri: Union[Column, str] = Column(types.String, comment='接口路径')
    status_code: Union[Column, int] = Column(types.UInt32, comment='响应状态')
    duration: Union[Column, int] = Column(types.UInt32, comment='响应延迟ms')
    source_ip: Union[Column, IPv4Address] = Column(types.IPv4, comment='源IP')
    destination_ip: Union[Column, IPv4Address] = Column(types.IPv4, comment='目的IP')
