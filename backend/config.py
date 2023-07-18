"""
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
File Name   : config.py
Author      : jinming.yang
Description : 数据库连接信息等参数配置
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
"""
import os

env = os.environ.get

_HOST = env('HOST', '127.0.0.1')

# MySQL连接配置
_M_HOST = env('MYSQL_HOST', _HOST)
_M_PORT = int(env('MYSQL_PORT', 3306))
_M_USER = env('MYSQL_USERNAME', 'root')
_M_PWD = env('MYSQL_ROOT_PASSWORD')
_M_DB = env('MYSQL_DATABASE')
DATABASE_OLTP_URI = f'mysql+mysqlconnector://{_M_USER}:{_M_PWD}@{_M_HOST}:{_M_PORT}/{_M_DB}'
# ClickHouse连接配置
_C_HOST = env('CLICKHOUSE_HOST', _HOST)
_C_PORT = int(env('CLICKHOUSE_PORT', 9000))
_C_USER = env('CLICKHOUSE_ADMIN_USER', 'default')
_C_PWD = env('CLICKHOUSE_ADMIN_PASSWORD')
_C_DB = env('CLICKHOUSE_DATABASE')
DATABASE_OLAP_URI = f'clickhouse://{_C_USER}:{_C_PWD}@{_C_HOST}:{_C_PORT}/{_C_DB}'
# Redis连接配置
REDIS_HOST = env('REDIS_HOST', _HOST)
REDIS_PORT = int(env('REDIS_PORT', 6379))
REDIS_PWD = env('REDIS_PASSWORD')
# Kafka连接配置
_K_HOST = env('KAFKA_HOST', _HOST)
_K_PORT = int(env('KAFKA_PORT', 9092))
_K_SERVER = f'{_K_HOST}:{_K_PORT}'
KAFKA_CONSUMER_TIMEOUT = int(env('KAFKA_CONSUMER_TIMEOUT', 100))  # 批量获取时的超时时间
KAFKA_PRODUCER_CONFIG = {
    'bootstrap.servers': _K_SERVER,
    'security.protocol': env('KAFKA_PROTOCOL', 'PLAINTEXT'),
    'message.max.bytes': int(env('KAFKA_MESSAGE_MAX_BYTES', 1000000000)),
    'queue.buffering.max.messages': int(env('KAFKA_PRODUCER_QUEUE_SIZE', 1000)),
}
KAFKA_CONSUMER_CONFIG = {
    'auto.offset.reset': 'earliest',
    'group.id': env('KAFKA_GROUP', 'default'),
    'bootstrap.servers': _K_SERVER,
}
