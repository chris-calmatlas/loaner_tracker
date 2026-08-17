#!/bin/bash
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --clear --no-input
gunicorn loaner_tracker.wsgi