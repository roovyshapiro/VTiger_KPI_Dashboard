from django.shortcuts import render, redirect, HttpResponseRedirect
from django.http import HttpResponse
from django.utils import timezone
from django.utils.timezone import make_aware
from django.contrib.auth.decorators import login_required
from django.db.models import Q


from cases.models import Cases
from sales.models import Phone_call
from dev.models import Redmine_issues

#import datetime, json, os, calendar, holidays

def main(request, username):
    '''
    /user/{username} goes here
    '''
    all_cases = Cases.objects.all()
    all_calls = Phone_call.objects.all()
    all_issues = Redmine_issues.objects.all()
    user_has_calls = False
    user_has_cases = False
    user_has_issues = False

    user_data = {}
    user_data['cases'] = {}
    user_data['calls'] = {}
    user_data['issues'] = {}
    user_data['username'] = username

    user_issues = all_issues.filter(assigned_to_name = username)
    user_calls = all_calls.filter(assigned_username = username)
    print(user_calls)
    print(len(user_calls))
    if len(user_calls) > 0:
        user_has_calls = True
        user_data['calls']['all_calls'] = len(user_calls)


    user_data['all_users'] = []
    case_users = all_cases.values('assigned_username').distinct()
    redmine_users = all_issues.values('assigned_to_name').distinct()
    for user in case_users:
        if user['assigned_username'] != '':
            user_data['all_users'].append(user['assigned_username'])
            user_has_cases = True
    for user in redmine_users:
        if user['assigned_to_name'] != '':
            user_data['all_users'].append(user['assigned_to_name'])
            user_has_issues = True

    assigned_cases = all_cases.filter(assigned_username = username)
    closed_cases = assigned_cases.filter(Q(casestatus='Closed') | Q(casestatus='Resolved'))
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


    user_data['issues']['open_issues'] = user_issues.filter(~Q(status_name="Done") & ~Q(status_name="Resolved") & ~Q(status_name="Rejected") & ~Q(status_name="Out of date") & ~Q(status_name="Not relevant") & ~Q(status_name="Unreproducible") & ~Q(status_name="Duplicate") & ~Q(status_name="Already fixed"))
    user_data['issues']['closed_issues'] =user_issues.filter(Q(status_name="Done")  | Q(status_name="Resolved"))
    user_data['issues']['rejected_issues'] = user_issues.filter(Q(status_name="Rejected") | Q(status_name="Out of date") | Q(status_name="Not relevant") | Q(status_name="Unreproducible") | Q(status_name="Duplicate") | Q(status_name="Already fixed"))

    user_data['issues']['assigned'] = len(user_issues)

    if not user_has_cases:
        del user_data['cases']
    if not user_has_issues:
        del user_data['issues']
    if not user_has_calls:
        del user_data['calls']

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
    all_cases = Cases.objects.all()
    all_calls = Phone_call.objects.all()
    all_issues = Redmine_issues.objects.all()
    user_data = {}
    user_data['cases'] = {}
    user_data['calls'] = {}
    user_data['issues'] = {}

    user_data['all_users'] = []
    case_users = all_cases.values('assigned_username').distinct()
    redmine_users = all_issues.values('assigned_to_name').distinct()
    for user in case_users:
        if user['assigned_username'] != '':
            user_data['all_users'].append(user['assigned_username'])
            user_has_cases = True
    for user in redmine_users:
        if user['assigned_to_name'] != '':
            user_data['all_users'].append(user['assigned_to_name'])
            user_has_issues = True
    context = {
        'user_data': user_data,
    }
    return render(request, "sales/user.html", context)