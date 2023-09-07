"""
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
File Name   : classes.py
Author      : jinming.yang@qingteng.cn
Description : 工具类定义
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
"""
import json
import random
import string
from datetime import datetime
from ipaddress import IPv4Address

import redis
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from confluent_kafka import Consumer
from confluent_kafka import Producer
from sqlalchemy.engine import Row

from config import KAFKA_CONSUMER_CONFIG
from config import KAFKA_CONSUMER_TIMEOUT
from config import KAFKA_PRODUCER_CONFIG
from config import REDIS_HOST
from config import REDIS_PORT
from config import REDIS_PWD
from defines import *
from utils import logger
from .constants import Constants

_redis_pool = redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PWD, decode_responses=True)
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
        self._producers = {}

    def get_consumer(self, topic: str) -> Consumer:
        """
        为每个Topic创建单独的消费者
        Args:
            topic: Topic名称

        Returns:
            消费者对象
        """
        if topic not in self._consumers:
            self._consumers[topic] = Consumer(KAFKA_CONSUMER_CONFIG)
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
        if topic not in self._producers:
            self._producers[topic] = Producer(KAFKA_PRODUCER_CONFIG)
        return self._producers[topic]

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

    def produce(self, topic, data):
        """
        生产数据
        Args:
            topic: Topic名称
            data: 带发送的数据

        Returns:
            None
        """

        producer = self.get_producer(topic)
        producer.produce(topic=topic, value=json.dumps(data), callback=self.delivery_report)
        producer.poll(0)


class JSONExtensionEncoder(json.JSONEncoder):
    """
    处理枚举等各种无法JSON序列化的类型
    """

    def default(self, obj):
        if isinstance(obj, Enum):
            return obj.name
        if isinstance(obj, datetime):
            return obj.strftime(Constants.DEFINE_DATE_FORMAT)
        if isinstance(obj, Row):
            return dict(obj._mapping)
        if isinstance(obj, ModelTemplate):
            return obj.json()
        if isinstance(obj, IPv4Address):
            return str(obj)
        return json.JSONEncoder.default(self, obj)


class ImageCode:
    CODE_LEN = 4

    @staticmethod
    def rand_color():
        """
        生成用于绘制字符串的随机颜色(可以随意指定0-255之间的数字)
        """
        red = random.randint(32, 200)
        green = random.randint(22, 255)
        blue = random.randint(0, 200)
        return red, green, blue

    @staticmethod
    def gen_text():
        """
        生成4位随机字符串
        """
        # sample 用于从一个大的列表或字符串中，随机取得N个字符，来构建出一个子列表
        return ''.join(random.sample(string.ascii_letters, ImageCode.CODE_LEN))

    @staticmethod
    def draw_lines(draw, num, width, height):
        """
        绘制干扰线
        """
        for num in range(num):
            x1 = random.randint(0, width / 2)
            y1 = random.randint(0, height / 2)
            x2 = random.randint(0, width)
            y2 = random.randint(height / 2, height)
            draw.line(((x1, y1), (x2, y2)), fill='black', width=1)

    def draw_verify_code(self):
        """
        绘制验证码图片
        """
        code = self.gen_text()
        width, height = 120, 50  # 设定图片大小，可根据实际需求调整
        im = Image.new('RGB', (width, height), 'white')  # 创建图片对象，并设定背景色为白色
        font = ImageFont.truetype(font='arial.ttf', size=40)  # 选择使用何种字体及字体大小
        draw = ImageDraw.Draw(im)  # 新建ImageDraw对象

        # 绘制字符串
        for i in range(4):
            draw.text(
                (5 + random.randint(-3, 3) + 23 * i, 5 + random.randint(-3, 3)),
                text=code[i],
                fill=self.rand_color(),
                font=font
            )
            # self.draw_lines(draw, 4, width, height)  # 绘制干扰线
        # im.show()  # 如需临时调试，可以直接将生成的图片显示出来
        return im, code
