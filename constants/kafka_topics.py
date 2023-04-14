"""
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
File Name   : kafka_topics.py
Author      : jinming.yang
Description : Kafka中的Topic名称
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
"""
# KAFKA_API_REQUEST_LOGS需要和migration/olap/upgrade.sql中的api_request_logs_queue表的kafka_topic_list保持一致
KAFKA_API_REQUEST_LOGS = 'ApiRequestLogs'
