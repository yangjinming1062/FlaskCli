#!/bin/bash

sleep 10

migrate() {
  target_dir="./migrations"
  if [ -z "$(ls -A $target_dir)" ]; then
    echo "Init Migrations"
    mv "./migrations_init" "$target_dir"
    mkdir $target_dir/oltp/versions  # 防止没有目录生成迁移文件失败
    alembic -c $target_dir/oltp/alembic.ini revision --autogenerate
    alembic -c $target_dir/oltp/alembic.ini upgrade head
    python command.py init
    python command.py user --password=admin
  fi
}

migrate || {
		echo "迁移执行命令失败，请人工确认"
}
