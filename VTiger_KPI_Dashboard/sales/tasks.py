from __future__ import absolute_import, unicode_literals
from celery import Celery
from celery import shared_task
from django.utils import timezone
from django.utils.timezone import make_aware
from django.db.models import Q


from .models import Phone_call, Opportunities
import VTiger_API
import json, os, datetime

@shared_task
def get_opportunities(day='month'):
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
        "cf_potentials_qualifiedby": "68x9346603",
        "qualified_by_name": "Erick Amador",

    },
    opp_id = models.CharField(max_length=50)
    contact_id = models.CharField(max_length=50)
    opp_amount = models.CharField(max_length=50)

    opp_no = models.CharField(max_length=50)
    opp_name = models.CharField(max_length=250)
    opp_stage = models.CharField(max_length=50)

    createdtime = models.DateTimeField()
    modifiedtime = models.DateTimeField()

    created_user_id = models.CharField(max_length=50)
    modifiedby = models.CharField(max_length=50)
    assigned_user_id = models.CharField(max_length=50)

    qualified_by_id = models.CharField(max_length=50)
    qualified_by_name = models.CharField(max_length=50)

    assigned_username = models.CharField(max_length=75)
    assigned_groupname = models.CharField(max_length=75)

    current_stage_entry_time = models.DateTimeField()
    demo_scheduled_changed_at = models.DateTimeField()
    demo_given_changed_at = models.DateTimeField()
    quote_sent_changed_at = models.DateTimeField()
    pilot_changed_at = models.DateTimeField()
    needs_analysis_changed_at = models.DateTimeField()
    closed_lost_changed_at = models.DateTimeField()
    closed_won_changed_at = models.DateTimeField()

    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.assigned_username} - {self.opp_name} - {self.opp_no} - {self.date_modified.strftime("%Y-%m-%d %H:%M:%S")}'

    def modifiedtime_date(self):
        return self.modifiedtime.strftime('%Y-%m-%d')
    '''
    if day == 'Today':
        today_opp_list = retrieve_stats(module = 'Potentials')
    elif day == 'month':
        today_opp_list = retrieve_stats(module = 'Potentials', day='month')

    db_opps = Opportunities.objects.all()

    for opp in today_opp_list:
        #If the opp_id exists in the database, then the opp will be updated
        #If the opp_id doesn't exist, then the opp will be added to the db
        try:
            new_opp = db_opps.get(opp_id = opp['id'])
        except:
            new_opp = Opportunities()

        new_opp.opp_id = opp['id']
        new_opp.opp_url_id = opp['id'].replace('5x','')

        new_opp.contact_id = opp['contact_id']
        new_opp.opp_amount = opp['amount']
        new_opp.opp_no = opp['potential_no']
        new_opp.opp_name = opp['potentialname']
        new_opp.opp_stage = opp['sales_stage']

        new_opp.createdtime = make_aware(datetime.datetime.strptime(opp['createdtime'],'%Y-%m-%d %H:%M:%S'))
        new_opp.modifiedtime = make_aware(datetime.datetime.strptime(opp['modifiedtime'] ,'%Y-%m-%d %H:%M:%S'))

        new_opp.created_user_id = opp['created_user_id']
        new_opp.modifiedby = opp['modifiedby']
        new_opp.assigned_user_id = opp['assigned_user_id']

        new_opp.qualified_by_id = opp['cf_potentials_qualifiedby']
        new_opp.qualified_by_name = opp['qualified_by_name']

        new_opp.assigned_username = opp['assigned_username']
        new_opp.modified_username = opp['modified_username']
        new_opp.assigned_groupname = opp['assigned_groupname']

        if opp['current_stage_entry_time'] != '':
            new_opp.current_stage_entry_time = make_aware(datetime.datetime.strptime(opp['current_stage_entry_time'],'%Y-%m-%d %H:%M:%S'))
        else:
            new_opp.current_stage_entry_time = None

        if opp['cf_potentials_demoscheduledchangedat'] != '':
            new_opp.demo_scheduled_changed_at = make_aware(datetime.datetime.strptime(opp['cf_potentials_demoscheduledchangedat'],'%m-%d-%Y %H:%M %p'))
        else:
            new_opp.demo_scheduled_changed_at = None

        if opp['cf_potentials_demogivenchangedat'] != '':
            new_opp.demo_given_changed_at = make_aware(datetime.datetime.strptime(opp['cf_potentials_demogivenchangedat'],'%m-%d-%Y %H:%M %p'))
        else:
            new_opp.demo_given_changed_at = None

        if opp['cf_potentials_quotesentchangedat'] != '':
            new_opp.quote_sent_changed_at = make_aware(datetime.datetime.strptime(opp['cf_potentials_quotesentchangedat'],'%m-%d-%Y %H:%M %p')) 
        else:
            new_opp.quote_sent_changed_at = None

        if opp['cf_potentials_pilotchangedat'] != '':
            new_opp.pilot_changed_at = make_aware(datetime.datetime.strptime(opp['cf_potentials_pilotchangedat'],'%m-%d-%Y %H:%M %p'))
        else:
            new_opp.pilot_changed_at = None

        if opp['cf_potentials_needsanalysischangedat'] != '':
            new_opp.needs_analysis_changed_at = make_aware(datetime.datetime.strptime(opp['cf_potentials_needsanalysischangedat'],'%m-%d-%Y %H:%M %p'))
        else:
            new_opp.needs_analysis_changed_at = None

        if opp['cf_potentials_closedlostchangedat'] != '':
            new_opp.closed_lost_changed_at = make_aware(datetime.datetime.strptime(opp['cf_potentials_closedlostchangedat'],'%m-%d-%Y %H:%M %p'))
        else:
            new_opp.closed_lost_changed_at = None

        if opp['cf_potentials_closedwonchangedat'] != '':
            new_opp.closed_won_changed_at = make_aware(datetime.datetime.strptime(opp['cf_potentials_closedwonchangedat'], '%m-%d-%Y %H:%M %p'))
        else: 
            new_opp.closed_won_changed_at = None

        new_opp.save()


def save_webhook_deal(webhook_data):
    '''
    {
        "opp_no": "POT4016",
        "opp_name": "test deal",
        "opp_amount": "150.00000000",
        "opp_stage": "Needs Analysis",
        "createdtime": "2024-01-05 20:44:40",
        "modifiedtime": "2024-01-05 21:37:59",
        "created_user": "Ryan Shanks",
        "modifiedby": "Ryan Shanks",
        "assigned_to": "65",
        "assigned_to_username": "rshanks@testbiz.io",
        "qualified_by": "Alejandro Folgers",
        "current_stage_entry_time": "2024-01-05 21:37:58",
        "demo_scheduled_changed_at": "01-05-2024 03:45 PM",
        "demo_given_changed_at": "01-05-2024 04:32 PM",
        "quote_sent_changed_at": "",
        "pilot_changed_at": "01-05-2024 04:35 PM",
        "needs_analysis_changed_at": "01-05-2024 04:37 PM",
        "closed_lost_changed_at": "",
        "closed_won_changed_at": "",
        "contact_name": "Christina Collander",
        "org_name": "BIZ - HQ",
        "assigned_groupname": "82",
        "cf_potentials_qualifiedby": "EMP87",
        "created_user2": "Ryan Shanks",
        "id": "5x2179843"
    }
    '''
    opp_id = webhook_data['id']

    # Check if the opportunity with given ID already exists
    try:
        existing_opp = Opportunities.objects.get(opp_id=opp_id)
    except Opportunities.DoesNotExist:
        # If the opportunity doesn't exist, create a new one
        existing_opp = Opportunities(opp_id=opp_id)

    # Update fields with new data
    existing_opp.opp_url_id = webhook_data['id'].replace('5x', '')
    existing_opp.contact_id = webhook_data['contact_name']
    existing_opp.opp_amount = webhook_data['opp_amount']

    existing_opp.opp_id = webhook_data['id']
    existing_opp.opp_no = webhook_data['opp_no']
    existing_opp.opp_name = webhook_data['opp_name']
    existing_opp.opp_stage = webhook_data['opp_stage']

    existing_opp.createdtime = make_aware(datetime.datetime.strptime(webhook_data['createdtime'],'%Y-%m-%d %H:%M:%S'))
    existing_opp.modifiedtime = make_aware(datetime.datetime.strptime(webhook_data['modifiedtime'] ,'%Y-%m-%d %H:%M:%S'))

    existing_opp.created_user_id = webhook_data['created_user2']
    existing_opp.modifiedby = webhook_data['modifiedby']
    existing_opp.assigned_user_id = webhook_data['assigned_to']

    existing_opp.qualified_by_id = webhook_data['cf_potentials_qualifiedby']
    existing_opp.qualified_by_name = webhook_data['qualified_by']

    existing_opp.assigned_username = webhook_data['assigned_to_username']
    existing_opp.modified_username = webhook_data['modifiedby']
    existing_opp.assigned_groupname = webhook_data['assigned_groupname']

    if webhook_data['current_stage_entry_time'] != '':
        existing_opp.current_stage_entry_time = make_aware(datetime.datetime.strptime(webhook_data['current_stage_entry_time'],'%Y-%m-%d %H:%M:%S'))
    else:
        existing_opp.current_stage_entry_time = None

    if webhook_data['demo_scheduled_changed_at'] != '':
        existing_opp.demo_scheduled_changed_at = make_aware(datetime.datetime.strptime(webhook_data['demo_scheduled_changed_at'],'%m-%d-%Y %H:%M %p'))
    else:
        existing_opp.demo_scheduled_changed_at = None

    if webhook_data['demo_given_changed_at'] != '':
        existing_opp.demo_given_changed_at = make_aware(datetime.datetime.strptime(webhook_data['demo_given_changed_at'],'%m-%d-%Y %H:%M %p'))
    else:
        existing_opp.demo_given_changed_at = None

    if webhook_data['quote_sent_changed_at'] != '':
        existing_opp.quote_sent_changed_at = make_aware(datetime.datetime.strptime(webhook_data['quote_sent_changed_at'],'%m-%d-%Y %H:%M %p')) 
    else:
        existing_opp.quote_sent_changed_at = None

    if webhook_data['pilot_changed_at'] != '':
        existing_opp.pilot_changed_at = make_aware(datetime.datetime.strptime(webhook_data['pilot_changed_at'],'%m-%d-%Y %H:%M %p'))
    else:
        existing_opp.pilot_changed_at = None

    if webhook_data['needs_analysis_changed_at'] != '':
        existing_opp.needs_analysis_changed_at = make_aware(datetime.datetime.strptime(webhook_data['needs_analysis_changed_at'],'%m-%d-%Y %H:%M %p'))
    else:
        existing_opp.needs_analysis_changed_at = None

    if webhook_data['closed_lost_changed_at'] != '':
        existing_opp.closed_lost_changed_at = make_aware(datetime.datetime.strptime(webhook_data['closed_lost_changed_at'],'%m-%d-%Y %H:%M %p'))
    else:
        existing_opp.closed_lost_changed_at = None

    if webhook_data['closed_won_changed_at'] != '':
        existing_opp.closed_won_changed_at = make_aware(datetime.datetime.strptime(webhook_data['closed_won_changed_at'], '%m-%d-%Y %H:%M %p'))
    else: 
        existing_opp.closed_won_changed_at = None

    # Save the opportunity
    existing_opp.save()



@shared_task
def get_phonecalls(day='Today'):
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
    if day == 'Today':
        today_phonecall_list = retrieve_stats(module = 'PhoneCalls')
    elif day == 'month':
        today_phonecall_list = retrieve_stats(module = 'PhoneCalls', day='month')

    db_phonecalls = Phone_call.objects.all()

    for phone_call in today_phonecall_list:
        #If the phone_call_id exists in the database, then the phone_call will be updated
        #If the phone_call_id doesn't exist, then the phone_call will be added to the db
        try:
            new_phone_call = db_phonecalls.get(phonecall_id = phone_call['id'])
        except:
            new_phone_call = Phone_call()               

        new_phone_call.phonecall_id = phone_call['id']
        new_phone_call.phonecall_url_id = phone_call['id'].replace('43x','')

        new_phone_call.customer = phone_call['customer']

        phone_call_start = make_aware(datetime.datetime.strptime(phone_call['createdtime'],'%Y-%m-%d %H:%M:%S'))
        new_phone_call.createdtime = phone_call_start
        new_phone_call.modifiedtime = make_aware(datetime.datetime.strptime(phone_call['modifiedtime'] ,'%Y-%m-%d %H:%M:%S'))

        #A 0 duration is retrieved as an empty string which can't be later converted to an int()
        if phone_call['totalduration'] == '':
            phone_call['totalduration'] = 0

        duration = datetime.timedelta(seconds=int(phone_call['totalduration']))
        new_phone_call.endtime = phone_call_start + duration

        new_phone_call.created_user_id = phone_call['created_user_id']
        new_phone_call.modifiedby = phone_call['modifiedby']
        new_phone_call.assigned_user_id = phone_call['assigned_user_id']

        new_phone_call.assigned_username = phone_call['assigned_username']
        new_phone_call.assigned_groupname = phone_call['assigned_groupname']
        new_phone_call.modified_username = phone_call['modified_username']

        new_phone_call.call_status = phone_call['callstatus']
        new_phone_call.direction = phone_call['direction']
        new_phone_call.total_duration = phone_call['totalduration']
        new_phone_call.customer_number = phone_call['customernumber']
        new_phone_call.recording_url = phone_call['recordingurl']

        new_phone_call.save()

def retrieve_stats(module = 'Potentials', day='Today'):
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
    vtigerapi = VTiger_API.Vtiger_api(credential_dict['username'], credential_dict['access_key'], credential_dict['host'])

    if module == 'Potentials':
        if day == 'Today':
            response = vtigerapi.retrieve_todays_cases(module = 'Potentials')
        elif day == 'month':
            response = vtigerapi.retrieve_todays_cases(module = 'Potentials', day='month')
    if module == 'PhoneCalls':
        if day == 'Today':
            response = vtigerapi.retrieve_todays_cases(module = 'PhoneCalls')
        elif day == 'month':
            response = vtigerapi.retrieve_todays_cases(module = 'PhoneCalls', day='month')

    return response