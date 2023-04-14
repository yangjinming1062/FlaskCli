"""
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
File Name   : config.py
Author      : jinming.yang
Description : 数据库连接信息等参数配置
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
"""
import os

env = os.environ.get

HOST = env('HOST_IP', '127.0.0.1')
# MySQL连接配置
MYSQL_HOST = env('MYSQL_HOST', HOST)
MYSQL_PORT = int(env('MYSQL_PORT', 3306))
MYSQL_USERNAME = env('MYSQL_USERNAME', 'root')
MYSQL_PASSWORD = env('MYSQL_ROOT_PASSWORD')
MYSQL_DATABASE = env('MYSQL_DATABASE')
DATABASE_MYSQL_URI = f'mysql+mysqlconnector://{MYSQL_USERNAME}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}'
# ClickHouse连接配置
CLICKHOUSE_HOST = env('CLICKHOUSE_HOST', HOST)
CLICKHOUSE_PORT = int(env('CLICKHOUSE_PORT', 9000))
CLICKHOUSE_USER = env('CLICKHOUSE_ADMIN_USER', 'default')
CLICKHOUSE_PASSWORD = env('CLICKHOUSE_ADMIN_PASSWORD')
CLICKHOUSE_DATABASE = env('CLICKHOUSE_DATABASE')
DATABASE_CLICKHOUSE_URI = f'clickhouse+native://{CLICKHOUSE_USER}:{CLICKHOUSE_PASSWORD}@{CLICKHOUSE_HOST}/{CLICKHOUSE_DATABASE}?allowMultiQueries=true'
# Redis连接配置
REDIS_HOST = env('REDIS_HOST', HOST)
REDIS_PORT = int(env('REDIS_PORT', 6379))
REDIS_PASSWORD = env('REDIS_PASSWORD')
# Kafka
KAFKA_HOST = env('KAFKA_HOST', HOST)
KAFKA_PORT = int(env('KAFKA_PORT', 9092))
KAFKA_GROUP = env('KAFKA_GROUP')
KAFKA_CONSUMER_TIMEOUT = int(env('KAFKA_CONSUMER_TIMEOUT', 100))  # 批量获取时的超时时间
KAFKA_PRODUCER_QUEUE_SIZE = int(env('KAFKA_PRODUCER_QUEUE_SIZE', 100))  # 每topic中满几个对象进行flush
KAFKA_MESSAGE_MAX_BYTES = int(env('KAFKA_MESSAGE_MAX_BYTES', 1000000000))
