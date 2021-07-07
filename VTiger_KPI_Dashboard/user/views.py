from django.shortcuts import render, HttpResponseRedirect
from django.http import HttpResponse
from django.utils import timezone
from django.utils.timezone import make_aware
from django.contrib.auth.decorators import login_required


#import datetime, json, os, calendar, holidays

@login_required()
def main(request, username):
    '''
    /user/{username} goes here
    '''
    user_data = {}

    user_data['username'] = username

    context = {
        'user_data': user_data,
    }
    return render(request, "sales/user.html", context) 

def user_home(request):
    '''
    If /user is navigated to without a user pre-selected
    '''
    user_data = {}
    user_data['username'] = False
    context = {
        'user_data': user_data,
    }
    return render(request, "sales/user.html", context) 