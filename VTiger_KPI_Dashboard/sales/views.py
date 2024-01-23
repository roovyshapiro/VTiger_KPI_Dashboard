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
from .serializers import DealSerializer
from rest_framework.decorators import api_view



from .models import Phone_call, Opportunities
import VTiger_API
import datetime, json, os, calendar, holidays


def main(request):
    '''
    The primary view for the Sales Dashboard where all the calculations take place.
    Celery populates the opportunities and phone calls from today periodically.
    '''
    sales_data = {}
    sales_data['all_sales_opps'] = Opportunities.objects.all().filter(assigned_groupname='Sales') | Opportunities.objects.all().filter(assigned_groupname='Sales Managers')

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
def webhook(request):
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