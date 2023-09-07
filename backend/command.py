"""
Usage:
    command.py user [--account=<admin>] [--username=<username>] [--password=<password>]
    command.py init
    command.py kafka
    command.py -h | --help
Options:
    --account=<admin>            初始账号 [default: admin]
    --username=<username>        初始用户名 [default: 默认管理员]
    --password=<password>        初始用户密码 [default: m/W*0-nS0t5]
"""
from docopt import docopt
from sqlalchemy.orm import Session

from defines import *
from utils import exceptions
from utils import generate_key


@exceptions()
def init_user(account, username, password):
    """
    添加初始用户
    Returns:

    """
    with Session(OLTPEngine) as session:
        uid = generate_key(account)  # 保证多环境管理员的id一致
        if user := session.get(User, uid):
            user.password = User.generate_hash(password)
        else:
            user = User()
            user.id = uid
            user.account = account
            user.username = username
            user.password = User.generate_hash(password)
            user.role = RoleEnum.Admin
            user.phone = '-'
            user.email = '-'
            session.add(user)
        session.commit()


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
    else:
        print('Missed Options')
    print('Success!')
