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


def get_opportunities():
    '''
    {
        "adjusted_amount": "999.00000000",
        "amount": "999.00000000",
        "assigned_groupname": "",
        "assigned_user_id": "19x55",
        "assigned_username": "James Johnkberg",
        "campaignid": "",
        "cf_potentials_chancetoclose": "Medium",
        "cf_potentials_closedlostchangedat": "",
        "cf_potentials_closedwonchangedat": "",
        "cf_potentials_demogivenchangedat": "12-08-2020 03:31 PM",
        "cf_potentials_demogivendate": "",
        "cf_potentials_demonotes": "",
        "cf_potentials_demoscheduledchangedat": "12-08-2020 03:27 PM",
        "cf_potentials_discoverynotes": "Looking to buy a product!",
        "cf_potentials_distributionid": "",
        "cf_potentials_industry": "",
        "cf_potentials_leadreferencenumber": "",
        "cf_potentials_needsanalysischangedat": "12-10-2020 10:36 AM",
        "cf_potentials_nextattempt": "2020-12-09",
        "cf_potentials_pilotchangedat": "",
        "cf_potentials_qualifiedby": "",
        "cf_potentials_quotesentchangedat": "12-08-2020 04:03 PM",
        "cf_potentials_timezone": "",
        "cf_potentials_website": "",
        "closingdate": "2021-01-21",
        "contact_id": "4x929209",
        "created_user_id": "19x55",
        "createdtime": "2020-12-08 21:27:04",
        "current_stage_entry_time": "2020-12-10 16:36:34",
        "description": "Customer is looking to buy a product.",
        "email": "",
        "forecast_amount": "849.15000000",
        "forecast_category": "Pipeline",
        "id": "5x929210",
        "isclosed": "0",
        "isconvertedfromlead": "1",
        "last_contacted_on": "",
        "last_contacted_via": "",
        "leadsource": "",
        "lost_reason": "",
        "modifiedby": "19x55",
        "modifiedtime": "2020-12-10 16:36:35",
        "nextstep": "",
        "opportunity_type": "",
        "pipeline": "Standard Sales Pipeline",
        "potential_no": "POT2122",
        "potentialname": "New Amazing Opportunity!",
        "prev_sales_stage": "",
        "probability": "85.000",
        "related_to": "3x929208",
        "sales_stage": "Needs Analysis",
        "source": "CRM",
        "starred": "",
        "tags": ""
    },
    '''
    pass

def get_phonecalls():
    '''
    {
        "CreatedTime": "2020-12-10 14:48:02",
        "assigned_groupname": "",
        "assigned_user_id": "19x27",
        "assigned_username": "Randall Hoberman",
        "billduration": "56",
        "billrate": "0.0000",
        "callid": "",
        "callstatus": "completed",
        "campaign_name": "",
        "campaign_number": "",
        "cases_id": "",
        "created_user_id": "19x27",
        "customer": "2x930718",
        "customernumber": "9545556480",
        "customertype": "Leads",
        "direction": "outbound",
        "disposition_name": "",
        "endtime": "2020-12-10 09:49:21",
        "gateway": "Asterisk",
        "id": "43x930719",
        "isclosed": "0",
        "modifiedby": "19x27",
        "modifiedtime": "2020-12-10 14:48:02",
        "notes": "",
        "potentials_id": "",
        "recordingurl": "http://voipserver.com:4001/recordings/90a897aeb4e34d129749ca436728ace7",
        "source": "CRM",
        "sourceuuid": "90a897aeb4e34d129749ca436728ace7",
        "starred": "",
        "starttime": "2020-12-10 09:48:02",
        "tags": "",
        "ticket_id": "",
        "totalduration": "56",
        "transcription": "",
        "transferred_number": "",
        "transferred_user": "",
        "user": "19x27"
    },
    '''
    pass

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