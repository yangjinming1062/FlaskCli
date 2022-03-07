# encoding:utf-8
import logging
import sys
import traceback
from datetime import datetime, date
from logging.handlers import BaseRotatingHandler
from os import mkdir, getcwd
from os.path import join, exists, split

import ujson

"""
提供日志记录功能
"""

log_dir = join(getcwd(), 'logs')
if not exists(log_dir):
    mkdir(log_dir)


class DayRotatingHandler(BaseRotatingHandler):
    """
    日志按天分割
    """

    def __init__(self, log_type, encoding=None, delay=False):
        log_type_dir = join(log_dir, log_type)
        if not exists(log_type_dir):
            mkdir(log_type_dir)
        self.date = date.today()
        self.suffix = "%Y-%m-%d.log"
        self.setLevel(logging.INFO)
        super(BaseRotatingHandler, self).__init__(join(log_type_dir, self.date.strftime(self.suffix)), 'a', encoding, delay)

    def shouldRollover(self, record):
        return self.date != date.today()

    def doRollover(self):
        if self.stream:
            self.stream.close()
            self.stream = None
        self.baseFilename = join(split(self.baseFilename)[0], date.today().strftime(self.suffix))
        self._open()


_InfoLogger = logging.getLogger("Info日志")
_InfoLogger.addHandler(DayRotatingHandler('Info'))

_WarnLogger = logging.getLogger("Warn日志")
_WarnLogger.addHandler(DayRotatingHandler('Warn'))

_ErrorLogger = logging.getLogger("Error日志")
_ErrorLogger.addHandler(DayRotatingHandler('Error'))

_ExceptionLogger = logging.getLogger("Exception日志")
_ExceptionLogger.addHandler(DayRotatingHandler('Exception'))


def _log(writer, base, msg):
    base['time'] = str(datetime.now())
    if isinstance(msg, str):
        base['content'] = msg
    elif isinstance(msg, BaseException):
        if isinstance(msg, KeyboardInterrupt):
            exit(0)
        else:
            if (tb := getattr(msg, "__traceback__", None)) is None:
                _, _, tb = sys.exc_info()
            content = [str(msg)]
            for ex in traceback.extract_tb(tb):
                content.append({
                    "file": ex.filename,
                    "line": ex.lineno,
                    "location": ex.line
                })
            base['content'] = content
    else:
        base['content'] = str(msg)
    try:
        writer.info(ujson.dumps(base, ensure_ascii=False))
    except Exception as ex:
        print(ex)


def info(msg, **kwargs):
    """
    记录Info级日志
    """
    _log(_InfoLogger, kwargs, msg)


def warn(msg, **kwargs):
    """
    记录Warning级日志
    """
    _log(_WarnLogger, kwargs, msg)


def error(msg, **kwargs):
    """
    记录Error级日志
    """
    _log(_ErrorLogger, kwargs, msg)


def exception(msg, **kwargs):
    """
    记录Exception级日志
    """
    _log(_ExceptionLogger, kwargs, msg)
