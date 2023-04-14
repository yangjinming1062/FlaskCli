"""
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
File Name   : business.py
Author      : jinming.yang
Description : 该文件中主要用于定义一些用户直接相关的业务类模型
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
"""
from sqlalchemy import Boolean
from sqlalchemy import or_
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash

from .base import *


class User(TPModelBase):
    """
    用户信息
    """
    __tablename__ = 'user'
    valid: Union[Column, bool] = Column(Boolean, default=True, comment='账号有效性')
    email: Union[Column, str] = Column(String(40), unique=True, comment='绑定的邮箱')
    phone: Union[Column, str] = Column(String(15), unique=True, comment='绑定的手机')
    account: Union[Column, str] = Column(String(40), nullable=False, unique=True, comment='用户名')
    username: Union[Column, str] = Column(String(40), comment='用户姓名')
    password: Union[Column, str] = Column(String(120), nullable=False, comment='密码：加密存储')

    @classmethod
    def search(cls, query_value):
        sql = select(cls).where(or_(cls.account == query_value, cls.phone == query_value, cls.email == query_value))
        return execute_sql(sql, tp_public_session, expect_list=False, keyword=0)

    @staticmethod
    def generate_hash(raw_password):
        return generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password, raw_password) or self.password == raw_password
