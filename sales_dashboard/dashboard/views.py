from django.shortcuts import render, HttpResponseRedirect
from django.http import HttpResponse
import VTiger_Sales_API
import json, os

# Create your views here.
def home_view(request):
    return HttpResponse('<h1>Dashboard Home</h1>')

def populate_db(request):
    user_stat_dict = retrieve_stats()
    print(user_stat_dict)
    return HttpResponseRedirect('/')

def retrieve_stats():
    '''
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
    user_stat_dict = vtigerapi.db_update()
    return user_stat_dict
