"""
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
File Name   : business.py
Author      : jinming.yang
Description : 该文件中主要用于定义一些用户直接相关的业务类模型
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
"""
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash

from .base import *


class User(OLTPModelBase):
    """
    用户信息
    """
    __tablename__ = 'user'
    valid: Mapped[bool] = mapped_column(default=True, comment='账号有效性')
    email: Mapped[str_m] = mapped_column(unique=True, comment='绑定的邮箱')
    phone: Mapped[str_s] = mapped_column(unique=True, comment='绑定的手机')
    account: Mapped[str_m] = mapped_column(unique=True, comment='用户名')
    username: Mapped[str_m] = mapped_column(comment='用户名')
    password: Mapped[str_l] = mapped_column(comment='密码')

    @staticmethod
    def generate_hash(raw_password):
        return generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password, raw_password) or self.password == raw_password
