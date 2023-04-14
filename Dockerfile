# 构建运行时环境
FROM python:3.10-slim-buster
# 设置时区
ENV TZ=Asia/Shanghai
# 设置语言
ENV LANG=zh_CN.UTF-8
# 设置工作目录
WORKDIR /opt/flask
# 安装依赖库
COPY ./requirements.txt ./requirements.txt
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
# 拷贝项目内容
COPY . .

EXPOSE 5000

# 单独只启动后端接口服务
CMD ["gunicorn", "app:app", "-c", "./run.py"]
