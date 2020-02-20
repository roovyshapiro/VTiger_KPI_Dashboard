#!/bin/bash

redis-server &
celery -A sales_dashboard worker &
celery -A sales_dashboard beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler &
python3 manage.py runserver 0.0.0.0:8000
