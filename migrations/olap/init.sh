#!/bin/bash

# 设置ClickHouse连接参数
CH_USER="default"
CH_PASSWORD="IDoNotKnow"
CH_DATABASE="default"

# 设置要执行的SQL文件路径
SQL_FILE="/docker-entrypoint-initdb.d/migrate.sql"

# 执行SQL文件
cat "$SQL_FILE" | clickhouse-client \
    --user="$CH_USER" \
    --password="$CH_PASSWORD" \
    --database="$CH_DATABASE" \
    --multiline \
    --multiquery