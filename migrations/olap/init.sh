#!/bin/bash

# 设置要执行的SQL文件路径
SQL_FILE="/docker-entrypoint-initdb.d/migrate.sql"

clickhouse-client --password="$CLICKHOUSE_ADMIN_PASSWORD" --user="$CLICKHOUSE_ADMIN_USER" --query="CREATE DATABASE IF NOT EXISTS $CLICKHOUSE_DATABASE"

# 执行SQL文件
cat "$SQL_FILE" | clickhouse-client \
    --user="$CLICKHOUSE_ADMIN_USER" \
    --password="$CLICKHOUSE_ADMIN_PASSWORD" \
    --database="$CLICKHOUSE_DATABASE" \
    --multiline \
    --multiquery