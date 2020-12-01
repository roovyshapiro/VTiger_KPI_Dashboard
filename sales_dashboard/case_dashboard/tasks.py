from __future__ import absolute_import, unicode_literals
from celery import Celery
from celery import shared_task
from django.utils import timezone
import datetime

from .models import Cases
import VTiger_Sales_API
import json, os

@shared_task
def populate_db_celery_cases():
    '''
    Example Case:

    {
        "age": "",
        "asset_id": "",
        "assigned_user_id": "19x91",
        "billable_time": "",
        "billing_service": "",
        "case_no": "CC21063",
        "casechannel": "",
        "casepriority": "Medium",
        "casestatus": "Open",
        "cf_1152": "",
        "cf_cases_autocommunicate": "1",
        "cf_cases_awaitingfeedback": "0",
        "contact_id": "4x316167",
        "created_user_id": "19x93",
        "createdtime": "2020-11-25 18:26:04",
        "current_state_entry_time": "2020-11-25 18:59:55",
        "customer_reply": "0",
        "deferred_date": "",
        "description": "Video needed in FMS for Truck 20",
        "email": "",
        "first_response_actualon": "",
        "first_response_expectedon": "2020-11-30 16:26:00",
        "first_response_status": "Time Left",
        "from_portal": "0",
        "group_id": "20x5",
        "id": "39x916810",
        "impact_area": "",
        "impact_type": "",
        "is_billable": "0",
        "is_billed": "0",
        "isclosed": "0",
        "last_responded_on": "",
        "modifiedby": "19x6",
        "modifiedtime": "2020-11-25 19:03:26",
        "parent_id": "3x220302",
        "product_id": "",
        "rate": "",
        "reassign_count": "0",
        "reopen_count": "0",
        "resolution": "",
        "resolution_time": "0.000",
        "resolution_type": "",
        "satisfaction_feedback": "",
        "satisfaction_index": "",
        "servicecontract_id": "",
        "servicelocation": "",
        "servicetype": "",
        "sla_actual_closureon": "",
        "sla_closureon": "2020-12-10 17:26:00",
        "slaid": "38x9",
        "slastatus": "Running",
        "source": "CRM",
        "starred": "",
        "tags": "",
        "time_spent": "0.594",
        "title": "Video needed in FMS for Truck 20",
        "total_time": "0",
        "wait_count": "",
        "work_location": "",
        "assigned_username" = "Bradley Spenkins",
        "assigned_groupname" = "Tech Support",
    },
    assigned_user_id = models.CharField(max_length=50)
    case_no = models.CharField(max_length=50)
    casestatus = models.CharField(max_length=50)
    contact_id = models.CharField(max_length=50)
    created_user_id = models.CharField(max_length=50)
    createdtime = models.CharField(max_length=50)
    group_id = models.CharField(max_length=50)
    case_id = models.CharField(max_length=50)
    modifiedby = models.CharField(max_length=50)
    modifiedtime = models.CharField(max_length=50)
    title = models.CharField(max_length=250)
    time_spent = models.CharField(max_length=50)
    assigned_username = models.CharField(max_length=75)
    assigned_groupname = models.CharField(max_length=75)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.case_no}: {self.date_modified.strftime("%Y-%m-%d %H:%M:%S")}'

        datetime.datetime.strptime('%Y-%m-%d %H:%M:%S', '2020-11-25 19:03:26')
     '''
    today_case_list = retrieve_case_data()
    db_cases = Cases.objects.all()

    for case in today_case_list:
        #If the case_id exists in the database, then the case will be updated
        #If the case_id doesn't exist, then the case will be added to the db
        try:
            new_case = db_cases.get(case_id = case['id'])
        except:
            new_case = Cases()

        new_case.assigned_user_id = case['assigned_user_id']
        new_case.case_no = case['case_no']
        new_case.casestatus = case['casestatus']
        new_case.contact_id = case['contact_id']
        new_case.created_user_id = case['created_user_id']
        new_case.createdtime = datetime.datetime.strptime(case['createdtime'],'%Y-%m-%d %H:%M:%S')
        new_case.group_id = case['group_id']
        new_case.case_id = case['id']
        new_case.modifiedby = case['modifiedby']
        new_case.modifiedtime = datetime.datetime.strptime(case['modifiedtime'] ,'%Y-%m-%d %H:%M:%S')
        new_case.title = case['title']
        new_case.time_spent = case['time_spent']
        new_case.assigned_username = case['assigned_username']
        new_case.assigned_groupname = case['assigned_groupname']

        new_case.save()

def retrieve_case_data():
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
    today_case_list = vtigerapi.retrieve_todays_cases()

    return today_case_list