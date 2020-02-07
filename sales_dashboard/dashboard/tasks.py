from __future__ import absolute_import, unicode_literals
from celery import Celery
from celery import shared_task
from .views import delete_all_items
from .models import Sales_stats

@shared_task
def test_shared_task():
    print('celery is working!')

@shared_task
def delete_database():
    Sales_stats.objects.all().delete()
    print('completed deleting')