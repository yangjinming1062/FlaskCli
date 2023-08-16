"""
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
File Name   : business.py
Author      : jinming.yang
Description : 业务逻辑相关模型
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
"""
import re
import string

from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash

from enums import *
from .base import *


class User(OLTPModelBase, TimeColumns):
    """
    用户信息
    """
    __tablename__ = 'user'
    role: Mapped[RoleEnum] = mapped_column(comment='角色')
    email: Mapped[str_m] = mapped_column(comment='邮箱')
    phone: Mapped[str_s] = mapped_column(comment='手机')
    username: Mapped[str_s] = mapped_column(comment='用户名')
    account: Mapped[str_m] = mapped_column(nullable=False, unique=True, comment='账号')
    password: Mapped[str_l] = mapped_column(comment='密码')
    valid: Mapped[bool] = mapped_column(default=True, comment='是否有效')

    @staticmethod
    def generate_hash(raw_password):
        return generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password, raw_password) or self.password == raw_password

    @staticmethod
    def valid_password(password):
        """
        校验密码是否合法
        """

        def _counter(text) -> int:
            """
            计算识别结果中的字符类型数量
            Args:
                text: 正则识别出的一段密钥文本

            Returns:
                类型计数
            """
            letter_flag = 0
            digit_flag = 0
            spec_flag = 0
            for char in text:
                if char in string.ascii_letters:
                    letter_flag = 1
                elif char in string.digits:
                    digit_flag = 1
                elif char in '(~!@$%^&*.)':
                    spec_flag = 1
                else:
                    raise ValueError('Invalid character')
            return letter_flag + digit_flag + spec_flag

        return 8 <= len(password) <= 16 and _counter(password) >= 2

    @staticmethod
    def valid_account(account):
        """
        校验账号是否合法
        """
        if len(account) > 50:
            return False
        for char in account:
            if char not in (string.digits + string.ascii_letters + '_-'):
                return False
        return True

    @staticmethod
    def valid_username(username):
        return len(username) <= 25

    @staticmethod
    def valid_phone(phone):
        """
        校验手机号是否合法
        """
        regex = r'\b(\+86)?(1[3-9]\d{9})|(1[3-9]\d{1}-\d{4}-\d{4})|(1[3-9]\d{1}-\d{3}-\d{5})\b'
        if re.match(regex, phone):
            return True
        return False

    @staticmethod
    def valid_email(mail):
        """
        校验邮箱是否合法
        """
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if re.match(regex, mail):
            return True
        return False
