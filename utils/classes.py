"""
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
File Name   : classes.py
Author      : jinming.yang@qingteng.cn
Description : 工具类定义
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
"""
import json

import redis
from confluent_kafka import Consumer
from confluent_kafka import Producer
from sqlalchemy import create_engine

from config import DATABASE_CLICKHOUSE_URI
from config import DATABASE_MYSQL_URI
from config import KAFKA_CONSUMER_TIMEOUT
from config import KAFKA_GROUP
from config import KAFKA_HOST
from config import KAFKA_MESSAGE_MAX_BYTES
from config import KAFKA_PORT
from config import KAFKA_PRODUCER_QUEUE_SIZE
from config import REDIS_HOST
from config import REDIS_PASSWORD
from config import REDIS_PORT
from utils import logger

OLTP_ENGINE = create_engine(DATABASE_MYSQL_URI, pool_size=150, pool_recycle=60)
OLAP_ENGINE = create_engine(DATABASE_CLICKHOUSE_URI)

_redis_pool = redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, decode_responses=True)
Redis = redis.Redis(connection_pool=_redis_pool)


# 单例基类
class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Kafka(metaclass=Singleton):

    def __init__(self):
        self._consumers = {}
        self._producer = {}
        self._producer_counter = {}

    def get_consumer(self, topic: str) -> Consumer:
        """
        为每个Topic创建单独的消费者
        Args:
            topic: Topic名称

        Returns:
            消费者对象
        """
        if topic not in self._consumers:
            self._consumers[topic] = Consumer(
                {
                    'auto.offset.reset': 'earliest',
                    'group.id': KAFKA_GROUP,
                    'bootstrap.servers': f'{KAFKA_HOST}:{KAFKA_PORT}',
                }
            )
            self._consumers[topic].subscribe([topic])
        return self._consumers[topic]

    def get_producer(self, topic):
        """
        为每个Topic创建单独的生产者
        Args:
            topic: Topic名称

        Returns:
            生产者对象
        """
        if topic not in self._producer:
            self._producer[topic] = Producer(
                {
                    'bootstrap.servers': f'{KAFKA_HOST}:{KAFKA_PORT}',
                    'security.protocol': 'PLAINTEXT',
                    'message.max.bytes': KAFKA_MESSAGE_MAX_BYTES,
                    'queue.buffering.max.messages': KAFKA_PRODUCER_QUEUE_SIZE,
                }
            )
            self._producer_counter[topic] = 0
        return self._producer[topic]

    @staticmethod
    def delivery_report(err, msg):
        """
        callback 消息向kafka写入时 获取状态
        """
        if err is not None:
            logger.error('Message delivery failed', err)

    def consume(self, topic, limit=None):
        """
        消费数据
        Args:
            topic: Topic名称
            limit: 批量获取数量（默认获取单条数据）

        Returns:
            json.loads后的数据
        """
        consumer = self.get_consumer(topic)
        if limit:
            # 超时 有多少信息返回多少信息 无消息返回空列表 []
            msgs = consumer.consume(num_messages=limit, timeout=KAFKA_CONSUMER_TIMEOUT)
            return [json.loads(msg.value().decode('utf-8')) for msg in msgs]
        else:
            while True:
                msg = consumer.poll(1.0)
                if msg is None or msg.error():
                    continue
                return json.loads(msg.value().decode('utf-8'))

    def produce(self, topic, data, flush=False):
        """
        生产数据
        Args:
            topic: Topic名称
            data: 带发送的数据
            flush: 是否在本次进行flush（默认在达到队列数量时自动提交）

        Returns:
            None
        """
        producer = self.get_producer(topic)
        producer.produce(topic=topic, value=json.dumps(data), callback=self.delivery_report)
        self._producer_counter[topic] += 1
        if self._producer_counter[topic] >= KAFKA_PRODUCER_QUEUE_SIZE or flush:
            self._producer_counter[topic] = 0
            producer.flush()
