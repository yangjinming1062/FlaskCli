"""
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
File Name   : __init__.py
Author      : jinming.yang
Description : 在init中导入各个子文件中的类、方法就可以直接从utils导入而无需关心具体路径了
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
"""
import os
import sys

from loguru import logger

from .classes import ExtensionJSONEncoder
from .classes import Kafka
from .classes import Redis
from .classes import Singleton
from .constants import Constants
from .functions import exceptions
from .functions import execute_sql
from .functions import shadow_str

# 日志记录
if not os.path.exists('./logs'):
    os.mkdir('./logs')
logger.add("./logs/DEBUG.log", retention="1 days", level="DEBUG")
logger.add("./logs/INFO.log", retention="1 days", level="INFO")
logger.add(sys.stdout, colorize=True, format="{time:YYYY-MM-DD HH:mm:ss}|<level>{message}</level>")
