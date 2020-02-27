from __future__ import absolute_import, unicode_literals
from celery import Celery
from celery import shared_task
from django.utils import timezone

from .models import Sales_stats, Phone_calls
import VTiger_Sales_API
import json, os

@shared_task
def populate_db_celery():
    '''
    Populates the database with stats from vtigerapi.retrieve_data()

    We retrieve a dictionary from VTiger that is formatted like this:
    {'gareth_bunkard': [0, 0, 0, 0, 0, 0, 0, '0', '2020-02-27 05:00:00', 'gareth_bunkard'], 
    'salvadore_louise': [0, 1, 3, 0, 0, 1, 0, '28', '2020-02-27 05:00:00', 'salvadore_louise'], 
    'shiminy_cartwheel': [0, 0, 0, 0, 0, 0, 0, '95', '2020-02-27 05:00:00', 'shiminy_cartwheel'], 
    'johnny_flinkson': [2, 1, 0, 1, 0, 0, 0, '74', '2020-02-27 05:00:00', 'johnny_flinkson']}

    {username: [demo scheduled, demo given, quote sent, pilot, needs analysis, closed won, closed lost, phone calls, date to start pulling data from, username']}
    '''
    user_stat_dict = retrieve_stats()
    stats = Sales_stats.objects.all()

    today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = timezone.now().replace(hour=23, minute=59, second=59, microsecond=0) 

    for value in user_stat_dict.values():
        #Attempt to find data in the database from today, if no objects are found, create new ones.
        sales_stat_query = stats.filter(user = value[9], date_created__gte=today_start, date_created__lte=today_end)
        if len(sales_stat_query) == 0:
            stat = Sales_stats()
        #If objects exists for today, update the existing ones instead of creating new ones.
        else:
            stat = sales_stat_query[0]

        stat.demo_scheduled =  value[0]
        stat.demo_given = value[1]
        stat.quote_sent  = value[2]
        stat.pilot  = value[3]
        stat.needs_analysis = value[4]
        stat.closed_won = value[5]
        stat.closed_lost =  value[6]

        stat.date = value[8]
        stat.user = value[9]
        stat.save()


        #Phone calls can be retrieved as a total number for the day, as the number doesn't change.
        #This is different than the opportunity sales stages as one opportunity can have multiple
        #sales stages changed in a day. Therefore, we attempt to retrieve the day's phone call entry
        #per user and update it. If we can't find any, then we create new ones.
        phone_query = Phone_calls.objects.filter(user = value[9], date_created__gte=today_start, date_created__lte=today_end)
        if len(phone_query) == 0:
            result = Phone_calls()
        else:
            result = phone_query[0]
        result.phone_calls = value[7]
        result.user = value[9]
        result.save()

def retrieve_stats():
    '''
    Prior to running this function,
    Create a file named 'credentials.json' with VTiger credentials
    and put it in the main sales_dashboard directory.
    It should have the following format:
    {"username": "(user)", "access_key": "(access_key)", "host": "(host)"}
    '''
    credentials_file = 'credentials.json'
    credentials_path = os.path.join(os.path.abspath('.'), credentials_file)
    with open(credentials_path) as f:
        data = f.read()
    credential_dict = json.loads(data)
    vtigerapi = VTiger_Sales_API.Vtiger_api(credential_dict['username'], credential_dict['access_key'], credential_dict['host'])
    user_stat_dict = vtigerapi.retrieve_data()

    return user_stat_dict