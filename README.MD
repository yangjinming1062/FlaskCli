![Flask](https://img.shields.io/badge/flask-v2.0+-blue)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-v1.4+-blue)
<br/>
<h1 align="center">
Flask后端项目框架
</h1>
<h4 align="center">专注于我的业务逻辑.</h4>

[//]: # (<h4 align="center">)

[//]: # (  <a href="https://placehold">Quickstart</a> |)

[//]: # (  <a href="https://placehold/">Docs</a> |)

[//]: # (  <a href="https://placehold">Tutorials</a> |)

[//]: # (</h4>)
<br/>

## 💡 功能特点

- 容器化：提供Docker及docker-compose文件，按需修改其中的参数即可使用（不改也能用）
- 轻量化：依赖的库尽可能的少，尤其flask相关，基本上仅依赖核心库即可运行
- 分层归类：实体、枚举、业务逻辑条理清晰
- 封装：接口的请求响应等常规内容均进行了统一的封装，专注于实现业务逻辑本身就好

## 🔮 未来预期

- 不定期想到哪些优化项再补充完善
- 可能会考虑加入WebSocket类接口，但是暂时没想好具体的应用场景

# ⚡ 快速开始

1. （可选）修改model等业务逻辑相关的代码
2. （可选）修改docker.env及docker-compose.yml等文件中诸如镜像名称等需要自定义的参数
3. 生成服务端镜像

```生成服务端镜像
docker build -t flaskcli:latest .
```

4. 通过docker-compose整体启动

```启动docker-compose
docker-compose -f docker-compose.yml up -d
```

# 📚 其他补充

## 项目说明

### 主要功能点

- 自动记录API调用日志【[app.py](app.py)-log_record】
- 自定义的接口鉴权及校验逻辑【[api.py](utils%2Fapi.py)-api_wrapper】
- 数据基类的封装【[base.py](models%2Fbase.py)】
- CRUD操作泛化接口【[crud.py](apis%2Fv1%2Fcrud.py)】

## DEBUG

app.py是项目的入口点，需要调试的时候直接运行app.py

## 数据迁移

迁移命令见根目录的initDB.sh脚本
