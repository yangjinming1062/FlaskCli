"""
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
File Name   : run.py
Author      : jinming.yang
Description : API后端接口的gunicorn启动配置文件
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
"""
capture_output = True
reuse_port = True
bind = '0.0.0.0:5000'
workers = 3
worker_class = 'gevent'
threads = 2
timeout = 120
accesslog = '-'
errorlog = '-'
max_requests = 300
max_requests_jitter = 10
