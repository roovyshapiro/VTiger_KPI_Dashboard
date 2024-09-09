from django.db import models
from django.utils import timezone
import VTiger_API
import json, os, datetime

class Phone_call(models.Model):
    '''
    Example Phone Call:
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
    createdtime = models.DateTimeField(null=True)
    modifiedtime = models.DateTimeField(null=True)
    endtime = models.DateTimeField(null=True)

    assigned_user_id = models.CharField(max_length=50)
    created_user_id = models.CharField(max_length=50)
    modified_by = models.CharField(max_length=50)
    assigned_username = models.CharField(max_length=50)
    assigned_groupname = models.CharField(max_length=50)
    modified_username = models.CharField(max_length=75, default='')

    phonecall_id = models.CharField(max_length=50)
    phonecall_url_id = models.CharField(max_length=50, default='')

    call_status = models.CharField(max_length=50)
    direction = models.CharField(max_length=50)
    total_duration = models.CharField(max_length=50)
    customer = models.CharField(max_length=50)
    customer_number = models.CharField(max_length=50)
    recording_url = models.CharField(max_length=250)

    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.assigned_username}: {self.customer_number} - {self.modifiedtime.strftime("%Y-%m-%d %H:%M:%S")}'



class Opportunities(models.Model):
    '''
    Example Opportunity:
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
    '''
    opp_id = models.CharField(max_length=50)
    opp_url_id = models.CharField(max_length=50, default='')
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

    qualified_by_id = models.CharField(max_length=50, null=True)
    qualified_by_name = models.CharField(max_length=50, null=True)

    assigned_username = models.CharField(max_length=75)
    assigned_groupname = models.CharField(max_length=75)
    modified_username = models.CharField(max_length=75, default='')

    current_stage_entry_time = models.DateTimeField(null=True)
    demo_scheduled_changed_at = models.DateTimeField(null=True)
    demo_given_changed_at = models.DateTimeField(null=True)
    quote_sent_changed_at = models.DateTimeField(null=True)
    pilot_changed_at = models.DateTimeField(null=True)
    needs_analysis_changed_at = models.DateTimeField(null=True)
    closed_lost_changed_at = models.DateTimeField(null=True)
    closed_won_changed_at = models.DateTimeField(null=True)

    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.assigned_username} - {self.opp_name} - {self.opp_no} - {self.date_modified.strftime("%Y-%m-%d %H:%M:%S")}'

    def modifiedtime_date(self):
        return self.modifiedtime.strftime('%Y-%m-%d')
    


class SMS(models.Model):
    '''
    Outbound SMS from Dialpad:
    {
        "id": 5417785884491776,
        "created_date": 1725563750776,
        "direction": "outbound",
        "event_timestamp": 1725563751909,
        "target": {
            "id": 6755239348502528,
            "type": "user",
            "name": "Jimbo Lowfer",
            "phone_number": "(512) 555-5555"
        },
        "contact": {
            "id": "http://www.google.com/m8/feeds/contacts/email/base/2688a7ca0e67324d",
            "name": "Jember Shender",
            "phone_number": "+15555551234"
        },
        "sender_id": 6755239348502528,
        "from_number": "+15125555555",
        "to_number": [
            "+15555551234"
        ],
        "mms": "FALSE",
        "is_internal": "FALSE",
        "message_status": "pending",
        "message_delivery_result": "NULL",
        "text": "This is an SMS sent from Dialpad",
        "text_content": "This is an SMS sent from Dialpad",
        "mms_url": "NULL"
    }

    Inbound SMS to Dialpad
    {
        "id": 5571516353560576,
        "created_date": 1725564299047,
        "direction": "inbound",
        "event_timestamp": 1725564299471,
        "target": {
            "id": 6755239348502528,
            "type": "user",
            "name": "Jimbo Lowfer",
            "phone_number": "(512) 555-5555"
        },
        "contact": {
            "id": "http://www.google.com/m8/feeds/contacts/email/base/2688a7ca0e67324d",
            "name": "Jember Shender",
            "phone_number": "+15555551234"
        },
        "sender_id": "NULL",
        "from_number": "+15555551234",
        "to_number": [
            "+15125555555"
        ],
        "mms": "FALSE",
        "is_internal": "FALSE",
        "message_status": "pending",
        "message_delivery_result": "NULL",
        "text": "This is a response text back to dialpad",
        "text_content": "This is a response text back to dialpad",
        "mms_url": "NULL"
    }
    '''
    sms_id = models.CharField(max_length=50)
    createdtime_epoch = models.CharField(max_length=50)
    createdtime = models.DateTimeField(null=True)
    direction = models.CharField(max_length=15)
    target_name = models.CharField(max_length=50)
    target_number = models.CharField(max_length=50)
    from_number = models.CharField(max_length=50)
    to_number = models.CharField(max_length=50)
    text = models.TextField()

    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.target_name} {self.createdtime.strftime("%Y-%m-%d %H:%M:%S")}: {self.to_number} - {self.text}'