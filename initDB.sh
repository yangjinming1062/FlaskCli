#!/bin/bash

sleep 10

migrate() {
  mkdir ./migrations/oltp/versions  # 防止没有目录生成迁移文件失败
  alembic -c ./migrations/oltp/alembic.ini revision --autogenerate
  alembic -c ./migrations/oltp/alembic.ini upgrade head
  python command.py init
  python command.py user --password=admin
}

migrate || {
		echo "迁移执行命令失败，请人工确认"
}
