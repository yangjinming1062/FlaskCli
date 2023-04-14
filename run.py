"""
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
File Name   : run.py
Author      : jinming.yang
Description : API后端接口的gunicorn启动配置文件
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
"""
workers = 12  # 定义同时开启的处理请求的进程数量，根据网站流量适当调整
worker_class = 'gevent'  # 采用gevent库，支持异步处理请求，提高吞吐量
bind = '0.0.0.0:5000'
threads = 5
timeout = 3000
