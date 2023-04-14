"""
Usage:
    command.py user [--account=<admin>] [--username=<username>] [--password=<password>]
    command.py init
    command.py -h | --help
Options:
    --account=<admin>            初始账号 [default: admin]
    --username=<username>        初始用户名 [default: 默认管理员]
    --password=<password>        初始用户密码 [default: m/W*0-nS0t5]
"""
from time import sleep

from docopt import docopt

from models import User


def init_user(account, username, password):
    """
    添加初始用户
    Returns:

    """
    for _ in range(10):
        try:
            if not User.search('admin'):
                User.create(username=username, account=account, password=password)
                print('Success!')
                return
        except:
            # 如果数据库还没有迁移，那么就等待一会儿再初始化
            sleep(10)
    print('Failed!')


def init_database():
    """
    初始化数据库
    TODO: 迁移只负责建表，如果需要向数据库中添加初始数据则通过该命令执行
    Returns:

    """
    pass


if __name__ == '__main__':
    options = docopt(__doc__, version='Command v1.0')
    if options['user']:
        init_user(options['--account'], options['--username'], options['--password'])
    elif options['init']:
        init_database()
