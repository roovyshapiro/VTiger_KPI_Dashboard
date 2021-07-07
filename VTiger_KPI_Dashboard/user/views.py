from django.shortcuts import render, redirect, HttpResponseRedirect
from django.http import HttpResponse
from django.utils import timezone
from django.utils.timezone import make_aware
from django.contrib.auth.decorators import login_required
from django.db.models import Q


from cases.models import Cases

#import datetime, json, os, calendar, holidays

def main(request, username):
    '''
    /user/{username} goes here
    '''
    user_data = {}
    user_data['cases'] = {}

    user_data['username'] = username

    user_data['all_users'] = []

    all_cases = Cases.objects.all()
    all_users = all_cases.values('assigned_username').distinct()
    for user in all_users:
        if user['assigned_username'] != '':
            user_data['all_users'].append(user['assigned_username'])

    assigned_cases = all_cases.filter(assigned_username = username)
    closed_cases = assigned_cases.filter(Q(casestatus='Closed') | Q(casestatus='esolved'))
    open_cases = assigned_cases.filter(~Q(casestatus='Closed') & ~Q(casestatus='Resolved'))
    user_data['cases']['assigned_cases'] = len(assigned_cases)
    user_data['cases']['closed_cases'] = len(closed_cases)
    user_data['cases']['open_cases'] = len(open_cases)


    user_data['cases']['feedback'] = {}
    user_data['cases']['feedback']['satisfied'] = 0
    user_data['cases']['feedback']['neutral'] = 0
    user_data['cases']['feedback']['not_satisfied'] = 0
    time_spent_list = []
    for case in assigned_cases:
        time_spent = case.time_spent
        if time_spent == '' or time_spent == ' ' or time_spent == None:
            time_spent = '0'
        time_spent_list.append(time_spent)
        if case.satisfaction_index == 'Satisfied':
            user_data['cases']['feedback']['satisfied'] += 1
        elif case.satisfaction_index == 'Neutral':
            user_data['cases']['feedback']['neutral'] += 1
        elif case.satisfaction_index == 'Not Satisfied':
            user_data['cases']['feedback']['not_satisfied'] += 1
        else:
            continue

    time_spent_list = [float(i) for i in time_spent_list]
    try:
        avg_time_spent = sum(time_spent_list) / len(time_spent_list)
        #Converts the time spent from a number of hours into something more human-readable
        #838.928 -> 34 Days, 22 Hours, 55 Minutes
        time_spent = float(avg_time_spent)
        avg_time_spent = f"{int(time_spent / 24)} Days, {int(time_spent % 24)} Hours, {int(((time_spent % 24) - int(time_spent % 24)) * 60)} Minutes"
    except ZeroDivisionError:
        avg_time_spent = 0
    user_data['cases']['avg_time_spent'] = avg_time_spent

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
    for user in all_users:
        if user['assigned_username'] != '':
            user_data['all_users'].append(user['assigned_username'])

    context = {
        'user_data': user_data,
    }
    return render(request, "sales/user.html", context)