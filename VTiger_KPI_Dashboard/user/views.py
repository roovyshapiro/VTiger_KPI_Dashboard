from django.shortcuts import render, redirect, HttpResponseRedirect
from django.http import HttpResponse
from django.utils import timezone
from django.utils.timezone import make_aware
from django.contrib.auth.decorators import login_required
from django.urls import reverse


from cases.models import Cases

#import datetime, json, os, calendar, holidays

def main(request, username):
    '''
    /user/{username} goes here
    '''
    user_data = {}

    user_data['username'] = username

    user_data['all_users'] = []

    all_cases = Cases.objects.all()
    all_users = all_cases.values('assigned_username').distinct()
    print(all_users)
    for user in all_users:
        if user['assigned_username'] != '':
            user_data['all_users'].append(user['assigned_username'])

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

    user_data['all_users'] = []

    all_cases = Cases.objects.all()
    all_users = all_cases.values('assigned_username').distinct()
    print(all_users)
    for user in all_users:
        if user['assigned_username'] != '':
            user_data['all_users'].append(user['assigned_username'])

    context = {
        'user_data': user_data,
    }
    return render(request, "sales/user.html", context)