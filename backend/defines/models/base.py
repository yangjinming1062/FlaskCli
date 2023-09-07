"""
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
File Name   : base.py
Author      : jinming.yang
Description : model基础信息定义
Model分为两类，
    - OLTP: 联机事务处理
    - OLAP: 联机事务处理
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
"""
from datetime import datetime
from typing import Optional
from uuid import uuid4

from clickhouse_driver import Client
from sqlalchemy import DateTime
from sqlalchemy import String
from sqlalchemy import create_engine
from sqlalchemy import func
from sqlalchemy import JSON
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm.collections import InstrumentedList
from sqlalchemy.orm.properties import ColumnProperty
from typing_extensions import Annotated

from config import DATABASE_OLAP_URI
from config import DATABASE_OLTP_URI

OLAPEngine = Client.from_url(DATABASE_OLAP_URI)
OLTPEngine = create_engine(DATABASE_OLTP_URI, pool_size=150, pool_recycle=60)

str_id = Annotated[str, mapped_column(String(16))]
str_small = Annotated[str, mapped_column(String(32))]
str_medium = Annotated[str, mapped_column(String(64))]
str_large = Annotated[str, mapped_column(String(128))]
str_huge = Annotated[str, mapped_column(String(256))]


class ModelTemplate:
    """
    提供公共方法的基类
    """

    @classmethod
    def get_columns(cls):
        """
        获取类中的全部数据库列的名称
        Returns:
            列名称列表
        """
        return [prop.key for prop in cls.__mapper__.iterate_properties if isinstance(prop, ColumnProperty)]

    @classmethod
    def to_property(cls, columns):
        """
        根据列名获取对应的列
        """
        return getattr(cls, columns) if isinstance(columns, str) else [getattr(cls, name) for name in columns]

    def json(self, excluded: set = None) -> dict:
        """
        将ORM实例转为可以序列化的dict对象
        Args:
            excluded: 需要忽略的列

        Returns:
            dict
        """
        result = {}
        ignored_fields = excluded or set()
        for prop in self.__mapper__.iterate_properties:
            if not isinstance(prop, ColumnProperty):
                continue
            if prop.key.startswith('_') or prop.key in ignored_fields:
                continue
            value = getattr(self, prop.key)
            if isinstance(value, InstrumentedList):
                result[prop.key] = [item.json() for item in value]
            elif isinstance(value, ModelTemplate):
                result[prop.key] = value.json()
            elif isinstance(prop.columns[0].type, JSON):
                result[prop.key] = value if value else None
            elif isinstance(prop.columns[0].type, DateTime):
                result[prop.key] = value if value else '-'
            else:
                result[prop.key] = value
        return result


class OLTPModelBase(DeclarativeBase, ModelTemplate):
    """
    OLTP模型基类
    """
    __abstract__ = True

    id: Mapped[str_id] = mapped_column(primary_key=True, default=lambda: uuid4().hex[-12:], comment='主键')


class OLAPModelBase(DeclarativeBase, ModelTemplate):
    """
    OLAP模型基类
    """
    __abstract__ = True

    id: Mapped[str_id] = mapped_column(primary_key=True, default=lambda: uuid4(), comment='主键')


class TimeColumns:
    """
    时间列基类
    """
    __abstract__ = True

    created_at: Mapped[datetime] = mapped_column(default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(onupdate=func.now(), nullable=True)
