<h1 align="center">Flask后端项目框架</h1>

# GraphQL接口文档
```
http://127.0.0.1:5000/api/v1/graphql
```

# 项目部署
## Docker部署
```
sudo apt-get install docker.io
sudo docker build -t xxx .
sudo docker run -d -p 5000:5000 --name xxx_container xxx
```

## 手动部署
### 安装项目依赖：
```
pip3 install -r requirements.txt
```

### 安装数据库
```
sudo apt install mysql-server
sudo apt redis
```

### 创建数据库
```
create user developer@'%' identified by 'password';
GRANT ALL PRIVILEGES ON *.* TO developer@'%' WITH GRANT OPTION;
flush privileges;
create schema <TODO> default character set utf8 collate utf8_general_ci;
```

### 启动API服务器：
```
gunicorn app:app -c run.py
```
