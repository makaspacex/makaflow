#!/bin/env bash
# 1. Make sure your models fits the current database schema. The easiest way to do it is trying to create new migrations:
python manage.py makemigrations

# 2. Clear the migration history for each app
python manage.py migrate --fake makaflow zero
python manage.py migrate --fake common zero

# 3. Remove the actual migration files.
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc" -delete

# 4. Create the initial migrations
python manage.py makemigrations

# 5. Fake the initial migration
python manage.py migrate --fake-initial








