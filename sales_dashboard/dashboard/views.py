from django.shortcuts import render
from django.http import HttpResponse
import VTiger_Sales_API

# Create your views here.
def home_view(request):
    return HttpResponse('<h1>Dashboard Home</h1>')

def populate_db(request):
    with open('credentials.json') as f:
        data = f.read()
    credential_dict = json.loads(data)
    vtigerapi = VTiger_Sales_API.Vtiger_api(credential_dict['username'], credential_dict['access_key'], credential_dict['host'])
    print(vtigerapi.db_update())
