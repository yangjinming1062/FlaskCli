"""
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
File Name   : constants.py
Author      : jinming.yang@qingteng.cn
Description : 常量定义
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
"""


class Constants:
    """
    常量定义：常量类型_常量名称
    """
    Topic_ReqLogs = 'ApiRequestLogs'  # 需要和migration/olap/upgrade.sql中的api_request_logs_queue表的kafka_topic_list保持一致
