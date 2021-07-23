#!/bin/bash

redis-server &
celery -A VTiger_KPI_Dashboard worker &
celery -A VTiger_KPI_Dashboard beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler &
celery -A VTiger_KPI_Dashboard flower &
python3 manage.py runserver --insecure 0.0.0.0:8000
