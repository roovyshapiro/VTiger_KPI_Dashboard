from django.db import models
from django.utils import timezone
import VTiger_Sales_API
import json, os

class Cases(models.Model):
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
    '''
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
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.case_no}: {self.date_modified.strftime("%Y-%m-%d %H:%M:%S")}'
