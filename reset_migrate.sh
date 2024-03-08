#!/bin/env bash

python manage.py showmigrations

python manage.py migrate --fake makaflow zero
python manage.py migrate --fake common zero

python manage.py showmigrations
# 清空migrations记录
# python manage.py dbshell
# TRUNCATE TABLE django_migrations;


find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc" -delete

python manage.py showmigrations

python manage.py makemigrations
python manage.py migrate --fake-initial







