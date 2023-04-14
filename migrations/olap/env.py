from logging.config import fileConfig

from alembic import context
from clickhouse_sqlalchemy.alembic.dialect import include_object
from clickhouse_sqlalchemy.alembic.dialect import patch_alembic_version
from sqlalchemy import engine_from_config
from sqlalchemy import pool

from config import DATABASE_CLICKHOUSE_URI
from models import APModelBase

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

config.set_main_option(
    'sqlalchemy.url',
    DATABASE_CLICKHOUSE_URI,
)
target_metadata = APModelBase.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    # this callback is used to prevent an auto-migration from being generated
    # when there are no changes to the schema
    # reference: http://alembic.zzzcomputing.com/en/latest/cookbook.html
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix='sqlalchemy.',
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata, include_object=include_object
        )

        with context.begin_transaction():
            patch_alembic_version(context)
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
