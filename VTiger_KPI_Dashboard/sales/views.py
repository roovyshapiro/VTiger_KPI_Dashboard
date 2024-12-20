from django.shortcuts import render, HttpResponseRedirect
from django.utils import timezone
from django.utils.timezone import make_aware
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from rest_framework import viewsets
from rest_framework.response import Response
from .serializers import DealSerializer, PhoneCallSerializer, SMSSerializer
from rest_framework.decorators import api_view



from .models import Phone_call, Opportunities, SMS
import VTiger_API
import datetime, json, os, calendar, holidays


def main(request):
    '''
    The primary view for the Sales Dashboard where all the calculations take place.
    Celery populates the opportunities and phone calls from today periodically.
    '''
    sales_data = {}
    sales_data['all_sales_opps'] = Opportunities.objects.all().filter(assigned_groupname='Sales') | Opportunities.objects.all().filter(assigned_groupname='Sales Managers')
    sales_data['all_sales_calls'] = Phone_call.objects.all().filter(assigned_groupname='Sales') | Phone_call.objects.all().filter(assigned_groupname='Sales Managers')

    #print(len(sales_data['all_sales_opps']))


    # Your data retrieval logic here (e.g., query your database)
    data = sales_data

    return render(request, "sales/sales2.html", {'data': data})


    context = {
        'sales_data': sales_data,
    }
    return render(request, "sales/sales2.html", context) 

class DealViewSet(viewsets.ModelViewSet):
    queryset = Opportunities.objects.all()
    serializer_class = DealSerializer

    def list(self, request):
        #start_date = self.request.query_params.get('start_date')
        #end_date = self.request.query_params.get('end_date')

        # Your filtering logic
        #opps = Opportunities.objects.filter(modifiedtime__date__gte=start_date, modifiedtime__date__lte=end_date).order_by('-modifiedtime')

        # Serialize the data
        serializer = DealSerializer(self.queryset, many=True)
        return Response(serializer.data)


class OpenDealsViewSet(viewsets.ModelViewSet):
    queryset = Opportunities.objects.exclude(opp_stage='Closed Lost').exclude(opp_stage='Closed Won').order_by('-modifiedtime')
    serializer_class = DealSerializer

class DateFilterDealViewSet(viewsets.ModelViewSet):
    queryset = Opportunities.objects.all()
    serializer_class = DealSerializer

    def list(self, request):
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        # Your filtering logic
        opps = Opportunities.objects.filter(modifiedtime__date__gte=start_date, modifiedtime__date__lte=end_date).order_by('-modifiedtime')

        # Serialize the data
        serializer = DealSerializer(opps, many=True)
        return Response(serializer.data)

class PhoneCallDateFilterViewSet(viewsets.ModelViewSet):
    queryset = Phone_call.objects.all()
    serializer_class = PhoneCallSerializer

    def list(self, request):
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        calls = Phone_call.objects.filter(createdtime__date__gte=start_date, createdtime__date__lte=end_date).order_by('-modifiedtime')

        # Serialize the data
        serializer = PhoneCallSerializer(calls, many=True)
        return Response(serializer.data)

class SMSDateFilterViewSet(viewsets.ModelViewSet):
    queryset = SMS.objects.all()
    serializer_class = SMSSerializer

    def list(self, request):
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        calls = SMS.objects.filter(createdtime__date__gte=start_date, createdtime__date__lte=end_date).order_by('-date_modified')

        # Serialize the data
        serializer = SMSSerializer(calls, many=True)
        return Response(serializer.data)


@login_required()
@staff_member_required
def populate_db(request):
    '''
    Populates the opportunities and phone calls databases.
    '''
    from sales.tasks import get_opportunities
    get_opportunities()

    return HttpResponseRedirect('/sales')

@csrf_exempt
def deal_webhook(request):
    '''
    Process incoming document updates from Outline's built in Webhook functionality.
    This replaces the need for celery tasks.
    '''
    if request.method == 'POST':
        #print(request.body)
        #print('\n')
        print(json.loads(request.body))
        data = json.loads(request.body)
        from .tasks import save_webhook_deal
        save_webhook_deal(data)
        #payload = json.loads(request.body)
        #print("Data received from Webhook is: ", payload)
        #print(request)
        #data = json.loads(request.body.decode('utf-8'))
        #print(data)
        #print(data)
        #print(request.body)
        #validation_token = request.headers.get('Validation-Token')

        #send_to_vtiger(payload)
        #response = HttpResponse(status=200)

        # add the Content-type header to the response
        #response['Content-type'] = 'application/json'
        #response['Validation-Token'] = validation_token

        # return the response
        #return response
        return HttpResponse(status=200)
    return HttpResponse(status=400)

@csrf_exempt
def call_webhook(request):
    '''
      {
    "master_call_id": null,
    "date_ended": 16828074,
    "voicemail_recording_id": null,
    "internal_number": "+132154",
    "call_recording_ids": [],
    "duration": 11989.972,
    "mos_score": 4.41,
    "entry_point_target": {},
    "proxy_target": {},
    "entry_point_call_id": null,
    "operator_call_id": null,
    "call_id": 461111840,
    "state": "hangup",
    "csat_score": null,
    "date_started": 168208017,
    "transcription_text": null,
    "direction": "outbound",
    "labels": [],
    "total_duration": 20056.427,
    "date_connected": 16884,
    "routing_breadcrumbs": [],
    "voicemail_link": null,
    "is_transferred": "FALSE",
    "public_call_review_share_link": "https://dialpad.com/shared/call/yx91bVOZxwcnjcCqz01qoUsO",
    "was_recorded": "FALSE",
    "date_rang": null,
    "target": {
      "phone": "+13",
      "type": "user",
      "id": 665136,
      "name": "Roovy Shapiro",
      "email": "roio"
    },
    "event_timestamp": 1682084129176,
    "contact": {
      "phone": "+2",
      "type": "local",
      "id": 5600392044183552,
      "name": "(619) 808-7922",
      "email": ""
    },
    "company_call_review_share_link": "https://dialpad.com/shared/call/2jdW0pGpCtoUMH4dcNv5tSeGskEL1jKLpHNl",
    "group_id": null,
    "external_number": "+1619"
  }
    
    '''
    if request.method == 'POST':
        payload = json.loads(request.body)
        #print("Data received from Webhook is: ", payload)
        #print(request)
        #print(request.body)
        validation_token = request.headers.get('Validation-Token')
        send_to_vtiger(payload)
        response = HttpResponse(status=200)
        # add the Content-type header to the response
        response['Content-type'] = 'application/json'
        response['Validation-Token'] = validation_token
        # return the response
        return response
        #return HttpResponse(status=200)
    return HttpResponse(status=400)

@csrf_exempt
def sms_webhook(request):
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
    print('SMS from Dialpad!')
    if request.method == 'POST':
        payload = json.loads(request.body)
        #print("Data received from Webhook is: ", payload)
        #print(request)
        #print(request.body)

        #Save the SMS to the DB
        from .tasks import save_dialpad_sms
        user_full_name = save_dialpad_sms(payload)

        send_sms_to_vtiger(payload, user_full_name)

        validation_token = request.headers.get('Validation-Token')
        #send_to_vtiger(payload)
        response = HttpResponse(status=200)
        # add the Content-type header to the response
        response['Content-type'] = 'application/json'
        response['Validation-Token'] = validation_token
        # return the response
        return response
        #return HttpResponse(status=200)
    return HttpResponse(status=400)

def send_to_vtiger(payload):
    with open('credentials.json') as f:
        data = f.read()
    credential_dict = json.loads(data)
    vtigerapi = VTiger_API.Vtiger_api(credential_dict['username'], credential_dict['access_key'], credential_dict['host'])
    vtigerapi.create_call(payload)

def send_sms_to_vtiger(payload, user_full_name):
    with open('credentials.json') as f:
        data = f.read()
    credential_dict = json.loads(data)
    vtigerapi = VTiger_API.Vtiger_api(credential_dict['username'], credential_dict['access_key'], credential_dict['host'])
    vtigerapi.create_sms(payload, user_full_name)

def test_method(request):
    print('test! Sales Views!')
    from .tasks import get_users_and_groups
    get_users_and_groups()
    return HttpResponseRedirect('/sales')

@login_required()
@staff_member_required
def populate_opp_month(request):
    '''
    Populates the opportunities and phone calls databases from the past 3 months.
    '''
    from sales.tasks import get_opportunities
    get_opportunities(day='month')

    return HttpResponseRedirect('/sales')

@login_required()
@staff_member_required
def get_new_users(request):
    with open('credentials.json') as f:
        data = f.read()
    credential_dict = json.loads(data)
    vtigerapi = VTiger_API.Vtiger_api(credential_dict['username'], credential_dict['access_key'], credential_dict['host'])
    vtigerapi.get_users_and_groups_file()
    return HttpResponseRedirect('/')
