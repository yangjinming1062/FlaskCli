# 构建运行时环境
FROM python:3.11-slim-buster
# 设置时区
ENV TZ=Asia/Shanghai
# 设置语言
ENV LANG=zh_CN.UTF-8
# 设置工作目录
WORKDIR /opt/flask
# 安装依赖
COPY ./backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
# 拷贝项目内容
COPY ./backend .
COPY ./initDB.sh .
RUN mv migrations migrations_init

EXPOSE 5000

# 单独只启动后端接口服务
CMD ["python", "./start.py"]
