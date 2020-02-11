from __future__ import absolute_import, unicode_literals
from celery import Celery
from celery import shared_task
from django.utils import timezone

from .models import Sales_stats
import VTiger_Sales_API
import json, os, datetime

@shared_task
def test_celery_beat():
    print('is this working?')


@shared_task
def populate_db_celery():
    '''
    Populates the database with stats from vtigerapi.db_update()
    demo_scheduled, demo_given, quote_sent, pilot, needs_analysis, closed_won, closed_lost, phone_calls, date, user
    {james_frinkle:[0, 1, 15, 0, 0, 3, 6, '215', '2020-01-28 21:30:00', 'james_frinkle']}
    '''
    user_stat_dict = retrieve_stats()
    for value in user_stat_dict.values():
        stat = Sales_stats()
        stat.demo_scheduled = value[0]
        stat.demo_given = value[1]
        stat.quote_sent = value[2]
        stat.pilot = value[3]
        stat.needs_analysis = value[4]
        stat.closed_won = value[5]
        stat.closed_lost = value[6]
        stat.phone_calls = value[7]
        stat.date = value[8]
        stat.user = value[9]
        stat.save()
    print('celery completed')


def retrieve_stats():
    '''
    Prior to running this function,
    Create a file named 'credentials.json' with VTiger credentials
    and put it in the main sales_dashboard directory.
    It should have the following format:
    {"username": "(user)", "access_key": "(access_key)", "host": "(host)"}
    '''
    #Get the most recently added item to the database
    try:
        latest_item = Sales_stats.objects.latest('date_created')
        #Current time in UTC
        now = timezone.now()
        #"date_created" audo_now_add is in UTC
        time_diff = now - latest_item.date_created
        time_diff_seconds = time_diff.total_seconds()
        catch_up_time = now - datetime.timedelta(seconds = time_diff_seconds)
        #If the most recent item in the DB was added more than 15 min ago
        if time_diff_seconds >= 900:
            #populate the database with the time frame from the last entry until now
            update_timespan = catch_up_time
        else:
            #populate the database with data from the last ten minutes.
            update_timespan = 'ten_min_ago'
    except:
        #If the database is empty, then the most recent item can't be checked
        update_timespan = 'today'
    

    credentials_file = 'credentials.json'
    credentials_path = os.path.join(os.path.abspath('.'), credentials_file)
    with open(credentials_path) as f:
        data = f.read()
    credential_dict = json.loads(data)
    vtigerapi = VTiger_Sales_API.Vtiger_api(credential_dict['username'], credential_dict['access_key'], credential_dict['host'])
    user_stat_dict = vtigerapi.retrieve_data(update_timespan)

    return user_stat_dict