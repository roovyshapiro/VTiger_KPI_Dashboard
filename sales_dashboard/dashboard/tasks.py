from __future__ import absolute_import, unicode_literals
from celery import Celery
from celery import shared_task
from django.utils import timezone
from django.utils.timezone import make_aware
from django.db.models import Q


from .models import Phone_call, Opportunities
import VTiger_Sales_API
import json, os, datetime

@shared_task
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
    opp_id = models.CharField(max_length=50)
    contact_id = models.CharField(max_length=50)

    opp_no = models.CharField(max_length=50)
    opp_name = models.CharField(max_length=250)
    opp_stage = models.CharField(max_length=50)

    createdtime = models.DateTimeField()
    modifiedtime = models.DateTimeField()

    created_user_id = models.CharField(max_length=50)
    modifiedby = models.CharField(max_length=50)
    assigned_user_id = models.CharField(max_length=50)

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
    today_opp_list = retrieve_stats(module = 'Potentials')
    db_opps = Opportunities.objects.all()

    for opp in today_opp_list:
        #If the opp_id exists in the database, then the opp will be updated
        #If the opp_id doesn't exist, then the opp will be added to the db
        try:
            new_opp = db_opps.get(opp_id = opp['id'])
        except:
            new_opp = Opportunities()

        new_opp.opp_id = opp['id']
        new_opp.contact_id = opp['contact_id']
        new_opp.opp_no = opp['potential_no']
        new_opp.opp_name = opp['potentialname']
        new_opp.opp_stage = opp['sales_stage']

        new_opp.createdtime = make_aware(datetime.datetime.strptime(opp['createdtime'],'%Y-%m-%d %H:%M:%S'))
        new_opp.modifiedtime = make_aware(datetime.datetime.strptime(opp['modifiedtime'] ,'%Y-%m-%d %H:%M:%S'))

        new_opp.created_user_id = opp['created_user_id']
        new_opp.modifiedby = opp['modifiedby']
        new_opp.assigned_user_id = opp['assigned_user_id']

        new_opp.assigned_username = opp['assigned_username']
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

@shared_task
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
    today_phonecall_list = retrieve_stats(module = 'PhoneCalls')
    db_phonecalls = Phone_call.objects.all()

    for phone_call in today_phonecall_list:
        #If the phone_call_id exists in the database, then the phone_call will be updated
        #If the phone_call_id doesn't exist, then the phone_call will be added to the db
        try:
            new_phone_call = db_phonecalls.get(phonecall_id = phone_call['id'])
        except:
            new_phone_call = Phone_call()               

        new_phone_call.phonecall_id = phone_call['id']
        new_phone_call.customer = phone_call['customer']

        phone_call_start = make_aware(datetime.datetime.strptime(phone_call['CreatedTime'],'%Y-%m-%d %H:%M:%S'))
        new_phone_call.createdtime = phone_call_start
        new_phone_call.modifiedtime = make_aware(datetime.datetime.strptime(phone_call['modifiedtime'] ,'%Y-%m-%d %H:%M:%S'))

        duration = datetime.timedelta(seconds=int(phone_call['totalduration']))
        new_phone_call.endtime = phone_call_start + duration

        new_phone_call.created_user_id = phone_call['created_user_id']
        new_phone_call.modifiedby = phone_call['modifiedby']
        new_phone_call.assigned_user_id = phone_call['assigned_user_id']

        new_phone_call.assigned_username = phone_call['assigned_username']
        new_phone_call.assigned_groupname = phone_call['assigned_groupname']

        new_phone_call.call_status = phone_call['callstatus']
        new_phone_call.direction = phone_call['direction']
        new_phone_call.total_duration = phone_call['totalduration']
        new_phone_call.customer_number = phone_call['customernumber']
        new_phone_call.recording_url = phone_call['recordingurl']

        new_phone_call.save()

def retrieve_stats(module = 'Potentials'):
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

    if module == 'Potentials':
        response = vtigerapi.retrieve_todays_cases(module = 'Potentials')
    if module == 'PhoneCalls':
        response = vtigerapi.retrieve_todays_cases(module = 'PhoneCalls')
    return response