from django.shortcuts import render, HttpResponseRedirect
from django.http import HttpResponse
from django.utils import timezone
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.csrf import csrf_exempt
import VTiger_API

import datetime, calendar
from .tasks import get_cases
from .models import Cases
import json,os

@login_required()
def main(request):
    '''
    Send all cases from the Cases db to the html template to be used in the html table.
    Send all unique group names in the context so that it can be used in a dropdown.
    Get the data from the form inputs like "group name" and filter the cases to be displayed.
    Retrieves user stats and date info and sends it to context.
    '''
    #Prepare the date and group that was chosen, so it can be displayed on the dashboard
    date_group_dict = {}

    full_cases = Cases.objects.all().order_by('-modifiedtime')

    #Returns dictionary with "assigned_groupname" as key, and the actual name as the value.
    #We pass these groups to the html to populate the drop down menu for filtering
    case_groups = full_cases.order_by().values('assigned_groupname').distinct()

    #We get the form submission from the drop down and use it to then filter the "full_case"
    #query set to only return and display the cases which match that group. If no group is 
    #selected, data is displayed from all groups and "All Groups" is sent to be displayed.
    group_request = request.GET.get('group_dropdown')

    #If "All Groups" is selected, a summary of open cases is provided
    all_groups_open = {}

    if group_request != '' and group_request is not None and group_request != 'All Groups':
        full_cases = full_cases.filter(assigned_groupname=group_request)
        date_group_dict['group'] = group_request
    else:
        date_group_dict['group'] = 'All Groups'
        for group in case_groups:
            group_cases = full_cases.filter(assigned_groupname=group['assigned_groupname'])
            group_open_cases = len(group_cases.filter(~Q(casestatus="Resolved") & ~Q(casestatus='Closed')))
            if group_open_cases != 0:
                all_groups_open[group['assigned_groupname']] = group_open_cases
    sorted_all_groups_open = sorted(all_groups_open.items(), key=lambda x: x[1], reverse=True)

    #Group Specific Charts
    historical_data = retrieve_historical_data(date_group_dict['group'], full_cases)
    month_comparison = month_comparison_data(date_group_dict['group'], full_cases)
    month_comparison_created = month_comparison_data(date_group_dict['group'], full_cases, case_status="Created")

    all_open_cases = {}
    all_open_cases['open_cases'] = len(full_cases.filter(~Q(casestatus="Resolved") & ~Q(casestatus="Closed")))
    all_open_cases['full_cases'] = full_cases.filter(~Q(casestatus="Resolved") & ~Q(casestatus="Closed"))

    date_request = request.GET.get('date_start')

    today, end_of_day, first_of_week, end_of_week, first_of_month, end_of_month = retrieve_dates(date_request)

    date_group_dict['today'] = today.strftime('%A, %B %d')
    date_group_dict['first_of_week'] = first_of_week.strftime('%A, %B %d')
    date_group_dict['end_of_week'] = end_of_week.strftime('%A, %B %d')
    date_group_dict['first_of_month'] = first_of_month.strftime('%A, %B %d')
    date_group_dict['end_of_month'] = end_of_month.strftime('%A, %B %d')


    case_stats_dict, sorted_user_closed, full_cases_day, created_cases_day, resolved_cases_day = retrieve_case_data(full_cases, today, end_of_day)
    case_stats_dict_week, sorted_user_closed_week, full_cases_week, created_cases_week, resolved_cases_week = retrieve_case_data(full_cases, first_of_week, end_of_week)
    case_stats_dict_month, sorted_user_closed_month, full_cases_month, created_cases_month, resolved_cases_month = retrieve_case_data(full_cases, first_of_month, end_of_month)

    user_assigned_total_open = retrieve_user_assigned_total(date_group_dict['group'], full_cases)
    sorted_user_assigned_total_open = sorted(user_assigned_total_open.items(), key=lambda x: x[1], reverse=True)

    #Retrieve user specific data for the entire month
    user_case_data = retrieve_user_data(full_cases,first_of_month, end_of_month)

    #We supply dictionaries of all the created cases to the html context so that we can easily pinpoint cases that were
    #created in that time frame. We highlight created cases in green and resolved cases in red.
    created_cases_dict_day = {}
    for item in created_cases_day:
        created_cases_dict_day[item.case_no] = item.case_no

    created_cases_dict_week = {}
    for item in created_cases_week:
        created_cases_dict_week[item.case_no] = item.case_no

    created_cases_dict_month = {}
    for item in created_cases_month:
        created_cases_dict_month[item.case_no] = item.case_no

    #We supply dictionaries of all the resolved cases to the html context so that we can easily pinpoint cases that were
    #resolved in that time frame. We highlight created cases in green and resolved cases in red.
    resolved_cases_dict_day = {}
    for item in resolved_cases_day:
        resolved_cases_dict_day[item.case_no] = item.case_no

    resolved_cases_dict_week = {}
    for item in resolved_cases_week:
        resolved_cases_dict_week[item.case_no] = item.case_no

    resolved_cases_dict_month = {}
    for item in resolved_cases_month:
        resolved_cases_dict_month[item.case_no] = item.case_no

    date_dict = {}
    #Min Max Values for Date Picker in base.html
    try:
        first_case = full_cases.order_by('modifiedtime').first().modifiedtime
        first_case = first_case.strftime('%Y-%m-%d')
        date_dict = {
            'first_db': first_case,
            'last_db': timezone.now().strftime('%Y-%m-%d'),
        }
    except AttributeError:
        populate_cases(request)

    #The VTiger hostnames are stored in the 'credentials.json' file.
    #The URLs themselves will look something like this:
    #"host_url_cases": "https://my_vtiger_instance_name.vtiger.com/index.php?module=Cases&view=Detail&record=", 
    credentials_file = 'credentials.json'
    credentials_path = os.path.join(os.path.abspath('.'), credentials_file)
    with open(credentials_path) as f:
        data = f.read()
    credential_dict = json.loads(data)
    urls = {}
    urls['cases_url'] = credential_dict['host_url_cases']


    context = {
        "case_groups":case_groups,
        "date_group_dict":date_group_dict,
        "all_open_cases":all_open_cases,
        'sorted_user_assigned_total_open':sorted_user_assigned_total_open,

        'user_case_data': user_case_data,
        'historical_data': historical_data,
        'month_comparison': month_comparison,
        'month_comparison_created' : month_comparison_created,

        "full_cases_day":full_cases_day,
        "case_stats_dict":case_stats_dict,
        "sorted_user_closed":sorted_user_closed,
        'created_cases_day':created_cases_dict_day,
        'resolved_cases_day':resolved_cases_dict_day,

        "full_cases_week":full_cases_week,
        "case_stats_dict_week":case_stats_dict_week,
        "sorted_user_closed_week":sorted_user_closed_week,
        'created_cases_week':created_cases_dict_week,
        'resolved_cases_week':resolved_cases_dict_week,

        "full_cases_month":full_cases_month,
        "case_stats_dict_month":case_stats_dict_month,
        "sorted_user_closed_month":sorted_user_closed_month,
        'created_cases_month':created_cases_dict_month,
        'resolved_cases_month':resolved_cases_dict_month,

        'date_dict':date_dict,
        'urls':urls,
        'sorted_all_groups_open': sorted_all_groups_open,
    }

    #If today is monday, and the user chooses to look at today's data, then the week's data will not
    #be shown. That is because if the current day is Monday, it will always be identical to the week's
    #data as no other data for days beyond today exist. 
    #However, if we look at a Monday in the past, then the data for the week will be different.
    #In addition, the week data also won't be shown if the week and month data is the same.
    #This occurs if the beginning of the week and the beginning of the month coincide
    if (today.weekday() == 0 and today.strftime('%Y-%m-%d') == timezone.now().strftime('%Y-%m-%d')) or \
        (len(full_cases_month) == len(full_cases_week) and len(created_cases_dict_week) == len(created_cases_dict_month)):
        del context["full_cases_week"]
        del context["case_stats_dict_week"]
        del context["sorted_user_closed_week"]

    #After returning the request, return the html file to go to, and the context to send to the html
    return render(request, "sales/cases.html", context) 


def retrieve_user_assigned_total(supplied_group, full_cases):
    '''
    How many opened cases are assigned to each user
    '''
    if supplied_group != 'All Groups':
        full_cases = full_cases.filter(assigned_groupname=supplied_group)

    #all_users = <QuerySet [{'assigned_username': 'James Fulcrumstein'}, {'assigned_username': 'Mary Littlelamb'}]
    all_users = full_cases.values('assigned_username').distinct()

    #user_dict = {'James Fulcrumstein':0, 'Mary Littlelamb':0, 'Kent Breakfield':0}
    user_dict = {}
    for user in all_users:
        user_dict[user['assigned_username']] = 0
    for case in full_cases.filter(~Q(casestatus="Resolved") & ~Q(casestatus="Closed")):
        if case.assigned_username in user_dict:
            user_dict[case.assigned_username] += 1

    #If a value is equal to 0, then we remove that key. 
    #No need to see which users don't have any currently assigned cases.
    #user_assigned_dict ={'James Fulcrumstein':3, 'Mary Littlelamb':5,}
    user_assigned_dict = {key:value for key, value in user_dict.items() if value != 0}
    return user_assigned_dict


def retrieve_case_data(full_cases, date_request, date_request_end):
    '''
    Returns data regards to the cases and users specified for the supplied time frame.
    Using a first of week and end of week for the "Shipping" group will retrieve data
    points that when rendered in the context to the HTML can look like this:
    
    WEEK
    Group: Shipping
    Monday, November 30 - Sunday, December 06
    Modified Cases: 33
    Created Cases: 8
    Resolved Cases: 15
    Kill Rate: 187%

    Closed Cases by User
    Jason Carlchuck  - 9
    Cornelius Pavlovsky - 6
    '''
    #Prepare calculated data to present as a simple summary overview of the cases
    #full_cases = Cases.objects.all()
    case_stats_dict = {}

    try:
        case_stats_opened = full_cases.filter(createdtime__gte=date_request, createdtime__lte=date_request_end)
        case_stats_dict['opened'] = len(case_stats_opened)
    except ValueError:
        case_stats_dict['opened'] = 0

    try:
        case_stats_modified = full_cases.filter(case_resolved__gte=date_request, case_resolved__lte=date_request_end)
        case_stats_closed = case_stats_modified.filter(Q(casestatus="Resolved") | Q(casestatus="Closed"))
        case_stats_dict['closed'] = len(case_stats_closed)
    except ValueError:
        case_stats_dict['closed'] = 0

    try:
        #Purpose of Modified cases is to show cases that were worked in a given time frame.
        #Since resolved cases become "closed" after a certain period of time, we don't want to show closed cases
        #that were modified. So ultimately we want to show for a given time frame - created cases, resolved cases,
        #And cases that were modified either because of being resolved, created or something else.
        case_stats = full_cases
        case_stats_modified = case_stats.filter(Q(modifiedtime__gte=date_request) & Q(modifiedtime__lte=date_request_end) & ~Q(casestatus="Closed"))
        case_stats_resolved = case_stats.filter(case_resolved__gte=date_request, case_resolved__lte=date_request_end)
        case_stats_created = case_stats.filter(createdtime__gte=date_request, createdtime__lte=date_request_end)
        case_stats = case_stats_modified | case_stats_resolved | case_stats_created
        case_stats_dict['modified'] = len(case_stats)
    except ValueError:
        case_stats_dict['modified'] = 0

    try:
        case_stats_dict['kill_rate'] = int((case_stats_dict['closed'] / case_stats_dict['opened']) * 100)
    except ValueError:
        case_stats_dict['kill_rate'] = int(0)
    except ZeroDivisionError:
        #If there are 0 opened cases and 3 closed cases, the kill rate will become 300%.
        case_stats_dict['kill_rate'] = int(case_stats_dict['closed'] * 100)

    #We calculate how many cases were closed per user and add it to the context to be displayed
    #all_users = <QuerySet [{'assigned_username': 'James Fulcrumstein'}, {'assigned_username': 'Mary Littlelamb'}]
    all_users = full_cases.order_by().values('assigned_username').distinct()

    #user_dict = {'James Fulcrumstein':0, 'Mary Littlelamb':0, 'Kent Breakfield':0}
    user_dict = {}
    for user in all_users:
        user_dict[user['assigned_username']] = 0

    #user_dict = {'James Fulcrumstein':3, 'Mary Littlelamb':5, 'Kent Breakfield':0}
    case_stats_modified = full_cases.filter(case_resolved__gte=date_request, case_resolved__lte=date_request_end)
    for case in case_stats_modified.filter(Q(casestatus="Resolved") | Q(casestatus="Closed")):
        if case.assigned_username in user_dict:
            user_dict[case.assigned_username] += 1

    #If a value is equal to 0, then we remove that key. 
    #No need to see which users didn't close any cases.
    #user_closed ={'James Fulcrumstein':3, 'Mary Littlelamb':5,}
    user_closed_dict = {key:value for key, value in user_dict.items() if value != 0}

    #Sort the dictionary so that the the dictionary with the highest value is displayed first
    #sorted_user_closed = [('Mary Littlelamb', 5),('James Fulcrumstein', 3)]
    sorted_user_closed = sorted(user_closed_dict.items(), key=lambda x: x[1], reverse=True)

    modified_with_closed_cases = full_cases.filter(modifiedtime__gte=date_request, modifiedtime__lte=date_request_end)
    modified_cases = modified_with_closed_cases.filter(~Q(casestatus="Closed"))
    resolved_cases = full_cases.filter(case_resolved__gte=date_request, case_resolved__lte=date_request_end)
    created_cases = full_cases.filter(createdtime__gte=date_request, createdtime__lte=date_request_end)

    #Combine all the Query sets.
    all_cases = modified_cases | created_cases | resolved_cases

    return case_stats_dict, sorted_user_closed, all_cases, created_cases, resolved_cases

def retrieve_user_data(full_cases,date_request, date_request_end):
    '''
    User based statistics:

    USER: Krinp Jristen
    AVG Time Spent: 34.37
    Open Assigned: 7
    Total Assigned: 14
    Total Resolved: 7
    Feedback - Satisfied 1
    Feedback - Neutral 0
    Feedback - Not Satisfied 0

    USER: Erin Horacefield
    AVG Time Spent: 27.21
    Open Assigned: 7
    Total Assigned: 13
    Total Resolved: 6
    Feedback - Satisfied 1
    Feedback - Neutral 0
    Feedback - Not Satisfied 0

    The returned user_cases is a dict of dicts which looks like this for each user:
    "Shawn Checkzberg":{
      "time_spent":[
         "99.956"
      ],
      "feedback":{
         "satisfied":0,
         "neutral":0,
         "not_satisfied":0
      },
      "assigned":1,
      "resolved":0,
      "assigned_all":1,
      "avg_time_spent":99.96
    }
    '''
    full_cases_date = full_cases.filter(createdtime__gte=date_request, createdtime__lte=date_request_end)
    open_cases = full_cases_date.filter(~Q(casestatus="Closed") & ~Q(casestatus="Resolved"))
    all_open_cases = full_cases.filter(~Q(casestatus="Closed") & ~Q(casestatus="Resolved"))
    closed_cases = full_cases.filter(case_resolved__gte=date_request, case_resolved__lte=date_request_end)


    all_users = full_cases_date.values('assigned_username').distinct()
    user_cases = {}

    for user in all_users:
        user_cases[user['assigned_username']] = {}
        user_cases[user['assigned_username']]['time_spent'] = []
        user_cases[user['assigned_username']]['feedback'] = {}
        user_cases[user['assigned_username']]['feedback']['satisfied'] = 0
        user_cases[user['assigned_username']]['feedback']['neutral'] = 0
        user_cases[user['assigned_username']]['feedback']['not_satisfied'] = 0

        for case in full_cases_date:
            if case.assigned_username == user['assigned_username']:
                time_spent = case.time_spent
                if time_spent == '' or time_spent == ' ' or time_spent == None:
                    time_spent = '0'
                user_cases[user['assigned_username']]['time_spent'].append(time_spent)
                if case.satisfaction_index == 'Satisfied':
                    user_cases[user['assigned_username']]['feedback']['satisfied'] += 1
                elif case.satisfaction_index == 'Neutral':
                    user_cases[user['assigned_username']]['feedback']['neutral'] += 1
                elif case.satisfaction_index == 'Not Satisfied':
                    user_cases[user['assigned_username']]['feedback']['not_satisfied'] += 1
                else:
                    continue


        user_cases[user['assigned_username']]['assigned'] = 0
        user_cases[user['assigned_username']]['resolved'] = 0
        for case in open_cases:
            if case.assigned_username == user['assigned_username']:
                user_cases[user['assigned_username']]['assigned'] += 1
        for case in closed_cases:
            if case.assigned_username == user['assigned_username']:
                user_cases[user['assigned_username']]['resolved'] += 1

        time_spent_list = [float(i) for i in user_cases[user['assigned_username']]['time_spent']]
        open_cases_len = len(all_open_cases.filter(assigned_username=user['assigned_username']))
        user_cases[user['assigned_username']]['assigned_all'] = open_cases_len
        try:
            avg_time_spent = sum(time_spent_list) / len(time_spent_list)
            #Converts the time spent from a number of hours into something more human-readable
            #838.928 -> 34 Days, 22 Hours, 55 Minutes
            time_spent = float(avg_time_spent)
            avg_time_spent = f"{int(time_spent / 24)} Days, {int(time_spent % 24)} Hours, {int(((time_spent % 24) - int(time_spent % 24)) * 60)} Minutes"
        except ZeroDivisionError:
            avg_time_spent = 0
        #user_cases[user['assigned_username']]['avg_time_spent'] = round(avg_time_spent, 2)
        user_cases[user['assigned_username']]['avg_time_spent'] = avg_time_spent

    return user_cases

def retrieve_dates(date_request):
    '''
    today = (datetime.datetime(2020, 12, 4, 0, 0) 
    end_of_day = (datetime.datetime(2020, 12, 4, 23, 59) 

    first_of_week = (datetime.datetime(2020, 11, 30, 0, 0) 
    end_of_week = (datetime.datetime(2020, 12, 6, 23, 59) 

    first_of_month = (datetime.datetime(2020, 12, 1, 0, 0)
    end_of_month = (datetime.datetime(2020, 12, 31, 23, 59)
    '''
    if date_request == '' or date_request == None:
        today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    else:
        today = datetime.datetime.strptime(date_request, '%Y-%m-%d')

    end_of_day = today.replace(hour=23, minute = 59, second = 59, microsecond = 0)

    #0 = monday, 5 = Saturday, 6 = Sunday 
    day = today.weekday()
    first_of_week = today + timezone.timedelta(days = -day)
    end_of_week = first_of_week + timezone.timedelta(days = 6)
    end_of_week = end_of_week.replace(hour = 23, minute = 59, second = 59)

    first_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    year = first_of_month.year
    month = first_of_month.month
    last_day = calendar.monthrange(year,month)[1]
    end_of_month = first_of_month.replace(day=last_day, hour=23, minute=59, second=59)

    return today, end_of_day, first_of_week, end_of_week, first_of_month, end_of_month

def retrieve_historical_data(supplied_group, full_cases_list):
    '''
    First, we go through all cases and find all the unique years based on created time.
    A dicitionary is generated for each year and each month.
    Ultimately, it looks like this:
    {
    2020:{
        1:{},
        2:{},
        3:{},
        ..
        12:{},
        }
    2021:{
        1:{}
        2:{}
        3:{}
        ..
        12:{},
        }
    }

    Each month dict has data associated for that month including 
    first and last day,
    year,
    month name,
    all groups created, resolved, kill rates,
    And a sub-dictionary of created, resolved, kill rate per group for that month.
    {
        1: {
            'first_of_month': datetime.datetime(2021, 1, 1, 0, 0, tzinfo=<UTC>), 
            'end_of_month': datetime.datetime(2021, 1, 31, 23, 59, 59, tzinfo=<UTC>), 
            'month': 'January', 
            'year': 2021, 
            'created_all': 282, 
            'resolved_all': 252
            'groups_data_month =  {
                    'Accounting': {'created': 53, 'resolved': 42, 'kill_rate': 79}, 
                    'Administrators': {'created': 19, 'resolved': 15, 'kill_rate': 78}, 
                    'Tech Support': {'created': 152, 'resolved': 136, 'kill_rate': 89}, 
                    'Shipping': {'created': 51, 'resolved': 50, 'kill_rate': 98}, 
                    ...
                    }
            }, 
        2: {
            'first_of_month': datetime.datetime(2021, 2, 1, 0, 0, tzinfo=<UTC>), 
            'end_of_month': datetime.datetime(2021, 2, 28, 23, 59, 59, tzinfo=<UTC>), 
            'month': 'February', 
            'year': 2021, 
            'created_all': 253, 
            'resolved_all': 212
            'groups_data_month = {
                    'Accounting': {'created': 53, 'resolved': 34, 'kill_rate': 64}, 
                    'Administrators': {'created': 41, 'resolved': 13, 'kill_rate': 31}, 
                    'Tech Support': {'created': 119, 'resolved': 123, 'kill_rate': 103}, 
                    'Shipping': {'created': 27, 'resolved': 38, 'kill_rate': 140},
                    ...
                    }
            },
    }

    Showing Total Created and Resolved Cases for each month in the years.
    Months will be at 0 if there are no cases in the DB for that month.
    (Unfortunately, there is no way to detect if a case has been deleted.
    Therefore, anytime a case has been deleted, all cases are deleted and
    re-retrieved starting from the earliest case.)

    January-2020 = C:0 R:0 K:0%
    February-2020 = C:30 R:14 K:46%
    March-2020 = C:546 R:448 K:82%
    April-2020 = C:340 R:273 K:80%
    May-2020 = C:284 R:281 K:98%
    June-2020 = C:371 R:313 K:84%
    July-2020 = C:340 R:341 K:100%
    August-2020 = C:299 R:262 K:87%
    September-2020 = C:354 R:367 K:103%
    October-2020 = C:363 R:368 K:101%
    November-2020 = C:254 R:268 K:105%
    December-2020 = C:261 R:294 K:112%
    January-2021 = C:282 R:252 K:89%
    February-2021 = C:253 R:212 K:83%
    March-2021 = C:198 R:74 K:37%
    April-2021 = C:0 R:0 K:0%
    May-2021 = C:0 R:0 K:0%
    June-2021 = C:0 R:0 K:0%
    July-2021 = C:0 R:0 K:0%
    August-2021 = C:0 R:0 K:0%
    September-2021 = C:0 R:0 K:0%
    October-2021 = C:0 R:0 K:0%
    November-2021 = C:0 R:0 K:0%
    December-2021 = C:0 R:0 K:0%
    '''
    full_cases = full_cases_list
    #Returns dictionary with "assigned_groupname" as key, and the actual name as the value.
    #case_groups = Cases.objects.values('assigned_groupname').distinct()
    case_groups = [{'assigned_groupname':supplied_group}]
    #get a list of all unique years which are used in cases
    case_years = []
    for case in full_cases:
        year = case.createdtime.year
        if year not in case_years:
            case_years.append(year)

    all_data = {}
    for year in case_years:
        #Each year gets associated to a dict for each month
        months = {i:{} for i in range(1,13)}
        all_data[year] = months

        #Generating the data per month
        for i in months:
            first_of_month = timezone.now().replace(month=i, year=year, day=1, hour=0, minute=0, second=0, microsecond=0)
            months[i]['first_of_month'] = first_of_month
            year = first_of_month.year
            month = first_of_month.month
            last_day = calendar.monthrange(year,month)[1]
            end_of_month = first_of_month.replace(day=last_day, hour=23, minute=59, second=59)
            months[i]['end_of_month'] = end_of_month

            months[i]['month'] = first_of_month.strftime('%B')
            months[i]['year'] = first_of_month.year
            created_cases = full_cases.filter(createdtime__gte=first_of_month, createdtime__lte=end_of_month)
            months[i]['created_all'] = len(created_cases)
            resolved_cases = full_cases.filter(case_resolved__gte=first_of_month, case_resolved__lte=end_of_month)
            months[i]['resolved_all'] = len(resolved_cases)
        
            try:
                months[i]['kill_rate_all'] = int((months[i]['resolved_all'] / months[i]['created_all']) * 100)
            except ValueError:
                months[i]['kill_rate_all'] = int(0)
            except ZeroDivisionError:
                #If there are 0 opened cases and 3 closed cases, the kill rate will become 300%.
                months[i]['kill_rate_all'] = int(months[i]['resolved_all'] * 100)

            #For each month, we show created, resolved and kill rate per group
            #Each month has a dict called "group_data_month" which looks like this:
            #{'Accounting': {'created': 53, 'resolved': 34, 'kill_rate': 64}, 
            # 'Administrators': {'created': 41, 'resolved': 13, 'kill_rate': 31}, 
            # 'Tech Support': {'created': 119, 'resolved': 123, 'kill_rate': 103},
            #  etc.
            #} 
            group_data_month = {}
            for group in case_groups:
                created_group_cases = created_cases.filter(assigned_groupname=group['assigned_groupname'])
                resolved_group_cases = resolved_cases.filter(assigned_groupname=group['assigned_groupname'])
                if len(created_group_cases) != 0:
                    group_data_month[group['assigned_groupname']] = {}
                    group_data_month[group['assigned_groupname']]['created'] = len(created_group_cases)
                    group_data_month[group['assigned_groupname']]['resolved'] = len(resolved_group_cases)
                    try:
                        group_data_month[group['assigned_groupname']]['kill_rate'] = int((len(resolved_group_cases) / len(created_group_cases)) * 100)
                    except ValueError:
                        group_data_month[group['assigned_groupname']]['kill_rate'] = int(0)
                    except ZeroDivisionError:
                        group_data_month[group['assigned_groupname']]['kill_rate'] = int(len(resolved_group_cases) * 100)

            months[i]['created_groups'] = group_data_month

    #Ultimately, we only want to display data that exists and not empty data for all future and past months
    #A new dict is created which only contains non-empty month data inside
    all_dict_non_empty = {i:{} for i in all_data}
    for year, months in all_data.items():
        for month, month_dict in months.items():
            if month_dict['created_all'] != 0 and month_dict['resolved_all'] != 0:
                all_dict_non_empty[year][month] = month_dict
    return(all_dict_non_empty)


def month_comparison_data(supplied_group, full_cases, case_status="Resolved"):
    '''
    {
    June':{
        'first_day': datetime.datetime(2021, 6, 1, 0, 0, tzinfo=<UTC>),
        'last_day': datetime.datetime(2021, 6, 30, 23, 59, 59, tzinfo=<UTC>), 
        'resolved': [6, 6, 6, 10, 0, 0, 6, 6, 7, 7, 6, 0, 0, 6, 4, 7, 3, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        }, 
    'May':{
        'first_day': datetime.datetime(2021, 5, 1, 0, 0, tzinfo=<UTC>), 
        'last_day': datetime.datetime(2021, 5, 31, 0, 0, tzinfo=<UTC>), 
        'resolved': [0, 0, 5, 7, 8, 7, 7, 0, 0, 7, 6, 9, 6, 5, 0, 0, 7, 3, 4, 11, 2, 0, 0, 19, 7, 2, 7, 2, 3, 0, 0]
    }, 
    'April': {
        'first_day': datetime.datetime(2021, 4, 1, 0, 0, tzinfo=<UTC>), 
        'last_day': datetime.datetime(2021, 4, 30, 0, 0, tzinfo=<UTC>), 
        'resolved': [9, 3, 0, 0, 11, 6, 3, 7, 4, 1, 0, 4, 1, 12, 3, 6, 0, 0, 20, 5, 9, 6, 12, 0, 1, 9, 5, 6, 5, 0]
        }, 
    'March': {
        'first_day': datetime.datetime(2021, 3, 1, 0, 0, tzinfo=<UTC>), 
        'last_day': datetime.datetime(2021, 3, 31, 0, 0, tzinfo=<UTC>), 
        'resolved': [10, 16, 3, 8, 0, 2, 1, 11, 9, 9, 6, 16, 0, 0, 11, 7, 9, 8, 1, 0, 0, 6, 5, 5, 4, 24, 0,0, 9, 4, 0]
        }
    }
    '''
    today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    first_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    year = first_of_month.year
    month = first_of_month.month
    last_day = calendar.monthrange(year,month)[1]
    end_of_month = first_of_month.replace(day=last_day, hour=23, minute=59, second=59)
    
    if supplied_group != 'All Groups':
        full_cases = full_cases.filter(assigned_groupname=supplied_group)

    comparison_data = {}

    last_day_of_previous_month1 = first_of_month - datetime.timedelta(days=1)
    first_day_of_previous_month1 = last_day_of_previous_month1.replace(day=1)
    
    last_day_of_previous_month2 = first_day_of_previous_month1 - datetime.timedelta(days=1)
    first_day_of_previous_month2 = last_day_of_previous_month2.replace(day=1)

    last_day_of_previous_month3 = first_day_of_previous_month2 - datetime.timedelta(days=1)
    first_day_of_previous_month3 = last_day_of_previous_month3.replace(day=1)

    comparison_data[first_of_month.strftime('%B')] = {}
    comparison_data[first_of_month.strftime('%B')]['first_day'] = first_of_month
    comparison_data[first_of_month.strftime('%B')]['last_day'] = end_of_month
    comparison_data[first_of_month.strftime('%B')]['resolved'] = []
    comparison_data[first_of_month.strftime('%B')]['created'] = []

    comparison_data[first_day_of_previous_month1.strftime('%B')] = {}
    comparison_data[first_day_of_previous_month1.strftime('%B')]['first_day'] = first_day_of_previous_month1
    comparison_data[first_day_of_previous_month1.strftime('%B')]['last_day'] = last_day_of_previous_month1
    comparison_data[first_day_of_previous_month1.strftime('%B')]['resolved'] = []
    comparison_data[first_day_of_previous_month1.strftime('%B')]['created'] = []

    comparison_data[first_day_of_previous_month2.strftime('%B')] = {}
    comparison_data[first_day_of_previous_month2.strftime('%B')]['first_day'] = first_day_of_previous_month2
    comparison_data[first_day_of_previous_month2.strftime('%B')]['last_day'] = last_day_of_previous_month2
    comparison_data[first_day_of_previous_month2.strftime('%B')]['resolved'] = []
    comparison_data[first_day_of_previous_month2.strftime('%B')]['created'] = []

    comparison_data[first_day_of_previous_month3.strftime('%B')] = {}
    comparison_data[first_day_of_previous_month3.strftime('%B')]['first_day'] = first_day_of_previous_month3
    comparison_data[first_day_of_previous_month3.strftime('%B')]['last_day'] = last_day_of_previous_month3
    comparison_data[first_day_of_previous_month3.strftime('%B')]['resolved'] = []
    comparison_data[first_day_of_previous_month3.strftime('%B')]['created'] = []

    #Makes a list of all days in the range of the beginning and end of the available days in db
    for month in comparison_data:
        if timezone.now().strftime('%B') == month:
            date_range = [comparison_data[month]['first_day'] + datetime.timedelta(days=x) for x in range(0, (timezone.now() - comparison_data[month]['first_day']).days + 1)]
        else:
            date_range = [comparison_data[month]['first_day'] + datetime.timedelta(days=x) for x in range(0, (comparison_data[month]['last_day'] - comparison_data[month]['first_day']).days + 1)]        
        for date in date_range:
            date_count = 0
            if case_status == "Resolved":
                for case in full_cases.filter(case_resolved__gte=comparison_data[month]['first_day'], case_resolved__lte=comparison_data[month]['last_day']):
                    if case.case_resolved.replace(hour=0, minute = 0, second=0,microsecond=0) == date:
                        date_count += 1
                if len(comparison_data[month]['resolved']) >= 1:
                    date_count = date_count + comparison_data[month]['resolved'][-1]
                comparison_data[month]['resolved'].append(date_count)            
            elif case_status == "Created":
                for case in full_cases.filter(createdtime__gte=comparison_data[month]['first_day'], createdtime__lte=comparison_data[month]['last_day']):
                    if case.createdtime.replace(hour=0, minute = 0, second=0,microsecond=0) == date:
                        date_count += 1
                if len(comparison_data[month]['created']) >= 1:
                    date_count = date_count + comparison_data[month]['created'][-1]
                comparison_data[month]['created'].append(date_count)
    return comparison_data

@login_required()
@staff_member_required
def populate_cases(request):
    get_cases()
    return HttpResponseRedirect("/cases")

@login_required()
@staff_member_required
def populate_all_cases(request):
    get_cases(get_all_cases=True)
    return HttpResponseRedirect("/cases")

@login_required()
@staff_member_required
def testing(request):
    '''
    The '/casestest' url calls this function which makes it great for testing.
    '''
    print('test')
    return HttpResponseRedirect("/")

@login_required()
@staff_member_required
def delete_all_cases(request):
    '''
    Delete all the cases in the database from today only.
    Convenient to reset the day's data without deleting previous days' data.
    '''
    today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = timezone.now().replace(hour=23, minute=59, second=59, microsecond=0)
    cases = Cases.objects.all().filter(date_modified__gte=today_start, date_modified__lte=today_end)

    cases.delete()

    #This deletes all items:
    #Cases.objects.all().delete()
    return HttpResponseRedirect('/cases')