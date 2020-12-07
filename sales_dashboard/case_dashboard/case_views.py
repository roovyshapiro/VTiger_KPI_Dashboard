from django.shortcuts import render, HttpResponseRedirect
from django.utils import timezone
from django.db.models import Q
import datetime, calendar
from .tasks import populate_db_celery_cases
from .models import Cases


def main_dashboard(request):
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
    case_groups = Cases.objects.values('assigned_groupname').distinct()

    #We get the form submission from the drop down and use it to then filter the "full_case"
    #query set to only return and display the cases which match that group. If no group is 
    #selected, data is displayed from all groups and "All Groups" is sent to be displayed.
    group_request = request.GET.get('group_dropdown')
    if group_request != '' and group_request is not None and group_request != '--Select Group--':
        full_cases = full_cases.filter(assigned_groupname=group_request)
        date_group_dict['group'] = group_request
    else:
        date_group_dict['group'] = 'All Groups'

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

    case_stats_dict, sorted_user_closed, full_cases_day = retrieve_case_data(full_cases, today, end_of_day)
    case_stats_dict_week, sorted_user_closed_week, full_cases_week = retrieve_case_data(full_cases, first_of_week, end_of_week)
    case_stats_dict_month, sorted_user_closed_month, full_cases_month = retrieve_case_data(full_cases, first_of_month, end_of_month)


    context = {
        "case_groups":case_groups,
        "date_group_dict":date_group_dict,
        "all_open_cases":all_open_cases,


        "full_cases_day":full_cases_day,
        "case_stats_dict":case_stats_dict,
        "sorted_user_closed":sorted_user_closed,

        "full_cases_week":full_cases_week,
        "case_stats_dict_week":case_stats_dict_week,
        "sorted_user_closed_week":sorted_user_closed_week,

        "full_cases_month":full_cases_month,
        "case_stats_dict_month":case_stats_dict_month,
        "sorted_user_closed_month":sorted_user_closed_month,
    }

    #After returning the request, return the html file to go to, and the context to send to the html
    return render(request, "dashboard/case_dashboard.html", context) 

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
    full_cases = full_cases.filter(modifiedtime__gte=date_request, modifiedtime__lte=date_request_end)
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
        case_stats = full_cases.filter(modifiedtime__gte=date_request, modifiedtime__lte=date_request_end)
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
    all_users = Cases.objects.values('assigned_username').distinct()

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

    return case_stats_dict, sorted_user_closed, full_cases

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

def populate_cases(request):
    populate_db_celery_cases()
    return HttpResponseRedirect("/cases")

def populate_all_cases(request):
    populate_db_celery_cases(get_all_cases=True)
    return HttpResponseRedirect("/cases")

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