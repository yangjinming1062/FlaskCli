"""
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
File Name   : config.py
Author      : jinming.yang
Description : 数据库连接信息等参数配置
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
"""
import os

_env = os.environ.get

_HOST = _env('HOST', '127.0.0.1')

# OLTP连接配置
_T_HOST = _env('OLTP_HOST', _HOST)
_T_PORT = int(_env('OLTP_PORT', 5432))
_T_USER = _env('POSTGRESQL_USERNAME', 'flaskcli')
_T_PWD = _env('POSTGRESQL_PASSWORD', 'IDoNotKnow')
_T_DB = _env('POSTGRESQL_DATABASE', 'flaskcli')
DATABASE_OLTP_URI = f'postgresql://{_T_USER}:{_T_PWD}@{_T_HOST}:{_T_PORT}/{_T_DB}'
# OLAP连接配置
_A_HOST = _env('OLAP_HOST', _HOST)
_A_PORT = int(_env('OLAP_PORT', 9000))
_A_USER = _env('CLICKHOUSE_ADMIN_USER', 'default')
_A_PWD = _env('CLICKHOUSE_ADMIN_PASSWORD', 'IDoNotKnow')
_A_DB = _env('CLICKHOUSE_DATABASE', 'flaskcli')
DATABASE_OLAP_URI = f'clickhouse://{_A_USER}:{_A_PWD}@{_A_HOST}:{_A_PORT}/{_A_DB}'
# Redis连接配置
REDIS_HOST = _env('REDIS_HOST', _HOST)
REDIS_PORT = int(_env('REDIS_PORT', 6379))
REDIS_PWD = _env('REDIS_PASSWORD', 'IDoNotKnow')
# Kafka连接配置
_K_HOST = _env('KAFKA_HOST', _HOST)
_K_PORT = int(_env('KAFKA_PORT', 9092))
_K_SERVER = f'{_K_HOST}:{_K_PORT}'
KAFKA_CONSUMER_TIMEOUT = int(_env('KAFKA_CONSUMER_TIMEOUT', 100))  # 批量获取时的超时时间
KAFKA_PRODUCER_CONFIG = {
    'bootstrap.servers': _K_SERVER,
    'security.protocol': _env('KAFKA_PROTOCOL', 'PLAINTEXT'),
    'message.max.bytes': int(_env('KAFKA_MESSAGE_MAX_BYTES', 1000000000)),
    'queue.buffering.max.messages': int(_env('KAFKA_PRODUCER_QUEUE_SIZE', 1000)),
}
KAFKA_CONSUMER_CONFIG = {
    'auto.offset.reset': 'earliest',
    'group.id': _env('KAFKA_GROUP', 'default'),
    'bootstrap.servers': _K_SERVER,
}
# Flask
JSON_AS_ASCII = False
