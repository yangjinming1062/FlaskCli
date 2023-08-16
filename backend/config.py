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

# OLTP连接配置
_T_HOST = env('OLTP_HOST', _HOST)
_T_PORT = int(env('OLTP_PORT', 5432))
_T_USER = env('POSTGRESQL_USERNAME', 'postgres')
_T_PWD = env('POSTGRESQL_PASSWORD')
_T_DB = env('POSTGRESQL_DATABASE')
DATABASE_OLTP_URI = f'postgresql://{_T_USER}:{_T_PWD}@{_T_HOST}:{_T_PORT}/{_T_DB}'
# OLAP连接配置
_A_HOST = env('OLAP_HOST', _HOST)
_A_PORT = int(env('OLTP_PORT', 9000))
_A_USER = env('CLICKHOUSE_ADMIN_USER', 'default')
_A_PWD = env('CLICKHOUSE_ADMIN_PASSWORD')
_A_DB = env('CLICKHOUSE_DATABASE')
DATABASE_OLAP_URI = f'clickhouse://{_A_USER}:{_A_PWD}@{_A_HOST}:{_A_PORT}/{_A_DB}'
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
