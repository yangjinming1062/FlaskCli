"""
该文件中主要用于定义一些用户直接相关的业务类模型
"""
from sqlalchemy import Boolean, ForeignKey
from sqlalchemy import or_
from sqlalchemy.dialects.mysql import JSON
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash

from .base import *


class User(ModelBase, ModelTemplate):
    """
    用户信息
    """
    __tablename__ = 'user'
    valid = Column(Boolean, default=True, comment='账号有效性')
    email = Column(String(40), unique=True, comment='绑定的邮箱')
    phone = Column(String(15), unique=True, comment='绑定的手机')
    account = Column(String(40), nullable=False, unique=True, comment='用户名')
    username = Column(String(40), comment='用户姓名')
    password = Column(String(120), nullable=False, comment='密码：加密存储')
    demo = relationship('Credential', back_populates='user', cascade="all, delete-orphan")

    @classmethod
    def search(cls, query_value):
        return cls.query(select(cls).where(or_(cls.account == query_value, cls.phone == query_value, cls.email == query_value)), False)

    @staticmethod
    def generate_hash(raw_password):
        return generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password, raw_password) or self.password == raw_password


class Demo(ModelBase, ModelTemplate):
    """
    用户的云平台认证信息
    """
    __tablename__ = 'demo'
    uid = Column(IdDefine, ForeignKey('user.id'), nullable=False)
    name = Column(String(100), comment='用户为该认证信息所提供的标识名称')
    plugin = Column(JSON, comment='复杂字段')
    user = relationship('User', back_populates='demo')

    @classmethod
    def search(cls, uid):
        return cls.query(select(cls).where(cls.uid == uid), True)
