from __future__ import absolute_import, unicode_literals
from celery import Celery
from celery import shared_task
from django.utils import timezone

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
        "work_location": ""
    },
    assigned_user_id = case['case_no']
    case_no = case['case_no']
    casestatus = case['case_no']
    contact_id = case['case_no']
    created_user_id = case['case_no']
    createdtime = case['case_no']
    group_id = case['case_no']
    case_id = case['case_no']
    modifiedby = case['case_no']
    modifiedtime = case['case_no']
    title = models.CharField(max_length=250)
    time_spent = case['case_no']
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.case_no}: {self.date_modified.strftime("%Y-%m-%d %H:%M:%S")}'
     '''
    today_case_list = retrieve_case_data()
    db_cases = Cases.objects.all()

    today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = timezone.now().replace(hour=23, minute=59, second=59, microsecond=0) 

    for case in today_case_list:
        #Attempt to find data in the database from today, if no objects are found, create new ones.
        #case_query = db_cases.filter(date_created__gte=today_start, date_created__lte=today_end)
        #if len(case_query) == 0:
        #    new_case = Cases()
        #If objects exists for today, update the existing ones instead of creating new ones.
        #else:
        #    new_case = case_query[0]

        new_case = Cases()

        new_case.assigned_user_id = case['assigned_user_id']
        new_case.case_no = case['case_no']
        new_case.casestatus = case['casestatus']
        new_case.contact_id = case['contact_id']
        new_case.created_user_id = case['created_user_id']
        new_case.createdtime = case['createdtime']
        new_case.group_id = case['group_id']
        new_case.case_id = case['id']
        new_case.modifiedby = case['modifiedby']
        new_case.modifiedtime = case['modifiedtime']
        new_case.title = case['title']
        new_case.time_spent = case['time_spent']

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