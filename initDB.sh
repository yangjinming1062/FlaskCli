#!/bin/bash

alembic -c ./migrations/oltp/alembic.ini revision --autogenerate
alembic -c ./migrations/oltp/alembic.ini upgrade head

python command.py init
python command.py user --password=admin
