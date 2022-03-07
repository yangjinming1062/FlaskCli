from secrets import token_urlsafe

from sqlalchemy import Column, String, create_engine
from sqlalchemy import select, insert, delete, update
from sqlalchemy.orm import Session, declarative_base, scoped_session, sessionmaker

from config import DATABASE_URI
from utils import logger

ModelBase = declarative_base()
engine = create_engine(DATABASE_URI, pool_size=150, pool_recycle=60)
graph_session = scoped_session(sessionmaker(autocommit=True, bind=engine))

IdDefine = String(32)


class ModelTemplate:
    """
    ORM基础类：定义了所有类的通用字段以及方法
    """
    id = Column(IdDefine, primary_key=True, default=lambda: token_urlsafe(24), comment='主键')
    query = graph_session.query_property()

    @staticmethod
    def execute(sql) -> bool:
        """
        执行更新、删除等无返回数据操作
        """
        with Session(engine) as session:
            try:
                session.execute(sql)
                session.commit()
                flag = True
            except Exception as ex:
                session.rollback()
                logger.exception(ex)
                flag = False
        return flag

    @classmethod
    def create(cls, **kwargs) -> str | None:
        created_id = None
        with Session(engine) as session:
            try:
                result = session.execute(insert(cls).values(**kwargs))
                created_id = result.inserted_primary_key[0]
                session.commit()
            except Exception as ex:
                session.rollback()
                logger.exception(ex)
        return created_id

    @classmethod
    def read(cls, query_id=None):
        """
        查询数据
        """
        with Session(engine) as session:
            if query_id:
                return session.execute(select(cls).where(cls.id == query_id)).scalar()
            else:
                return session.execute(select(cls)).scalars().all()

    @classmethod
    def update(cls, query_id, data):
        """
        更新数据
        """
        return cls.execute(update(cls).where(cls.id == query_id).values(**data))

    @classmethod
    def delete(cls, query_id) -> bool:
        """
        删除数据
        """
        with Session(engine) as session:
            try:
                if instance := session.execute(delete(cls).where(cls.id == query_id)).first():
                    session.delete(instance)  # 通过该方式可以级联删除子数据
                    session.commit()
                    flag = True
                else:
                    flag = False
            except Exception as ex:
                session.rollback()
                logger.exception(ex)
                flag = False
        return flag

    @staticmethod
    def shadow(source, head=3, tail=2) -> str:
        """
        对敏感信息进行部分隐藏，只暴露头尾
        :param source: 待隐藏字符串
        :param head: 前面暴露几个字符
        :param tail: 后面暴露几个字符
        :return:
        """
        if source is None:
            return ""
        if len(source) < head + tail:
            return source
        return f"{source[:head]}**{source[-tail:]}"
