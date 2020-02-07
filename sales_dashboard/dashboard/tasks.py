from __future__ import absolute_import, unicode_literals
from celery import Celery
from celery import shared_task
from .models import Sales_stats
from django.utils import timezone
from django.db.models import Sum

@shared_task
def database_retrieve():
    Sales_stats.objects.all()
    today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = timezone.now().replace(hour=23, minute=59, second=59, microsecond=0)
    phone_calls_sum = Sales_stats.objects.all().filter(date__gte=today_start, date__lte=today_end).aggregate(Sum('phone_calls'))
    print(phone_calls_sum)
    print('completed database_retrieval')