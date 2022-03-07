# 构建运行时环境
FROM python:3.9

WORKDIR /opt/flask

RUN apt-get update \
    && apt-get -y install mysql-server redis

COPY . .

RUN pip3 install -r requirements.txt

VOLUME /opt/flask/logs

ENV LANG=zh_CN.UTF-8

EXPOSE 5000

CMD ["gunicorn", "app:app", "-c", "./run.py"]
