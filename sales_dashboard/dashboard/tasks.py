from __future__ import absolute_import, unicode_literals
from celery import Celery
from celery import shared_task
from django.utils import timezone

from .models import Sales_stats, Phone_calls
import VTiger_Sales_API
import json, os

@shared_task
def test_celery_beat():
    print('is this working?')


@shared_task
def populate_db_celery():
    '''
    Populates the database with stats from vtigerapi.retrieve_data()
    demo_scheduled, demo_given, quote_sent, pilot, needs_analysis, closed_won, closed_lost, phone_calls, date, user
    {james_frinkle:[0, 1, 15, 0, 0, 3, 6, '215', '2020-01-28 21:30:00', 'james_frinkle']}
    '''
    user_stat_dict = retrieve_stats()
    stats = Sales_stats.objects.all()

    today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = timezone.now().replace(hour=23, minute=59, second=59, microsecond=0) 

    for value in user_stat_dict.values():
        sales_stat_query = stats.filter(user = value[9], date_created__gte=today_start, date_created__lte=today_end)
        #If there are no objects in the database, create new ones.
        if len(sales_stat_query) == 0:
            stat = Sales_stats()
            stat.demo_scheduled = value[0]
            stat.demo_given = value[1]
            stat.quote_sent = value[2]
            stat.pilot = value[3]
            stat.needs_analysis = value[4]
            stat.closed_won = value[5]
            stat.closed_lost = value[6]
        #If objects exists for today, update the existing ones instead of creating new ones.
        else:
            stat = sales_stat_query[0]
            stat.demo_scheduled = str(int(stat.demo_scheduled) + value[0])
            stat.demo_given = str(int(stat.demo_given) + value[1])
            stat.quote_sent = str(int(stat.quote_sent) + value[2])
            stat.pilot = str(int(stat.pilot) + value[3])
            stat.needs_analysis = str(int(stat.needs_analysis) + value[4])
            stat.closed_won = str(int(stat.closed_won) + value[5])
            stat.closed_lost = str(int(stat.closed_lost) + value[6])

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
    #Get the most recently added item to the database
    #and retrieve data from that point. The time frame for when
    #to retrieve new data is decided by the celery beat period task.
    #Wether its every 1, 5 or 10 minutes, this function will return
    #all the data point since the last entry in the database.
    try:
        latest_item = Sales_stats.objects.latest('date_created')
        update_timespan = latest_item.date_created
    except:
        #If the database is empty, then the most recent item can't be checked
        #We pass 'today' which vtigerapi.retrieve_data will use to gather
        #all data since the beginning of the day.
        update_timespan = 'today'    

    credentials_file = 'credentials.json'
    credentials_path = os.path.join(os.path.abspath('.'), credentials_file)
    with open(credentials_path) as f:
        data = f.read()
    credential_dict = json.loads(data)
    vtigerapi = VTiger_Sales_API.Vtiger_api(credential_dict['username'], credential_dict['access_key'], credential_dict['host'])
    user_stat_dict = vtigerapi.retrieve_data(update_timespan)

    return user_stat_dict