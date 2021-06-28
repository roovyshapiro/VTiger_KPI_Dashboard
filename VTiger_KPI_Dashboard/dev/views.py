from django.shortcuts import render, HttpResponseRedirect
from django.http import HttpResponse
from django.db.models import Q
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .tasks import get_issues
from .models import Redmine_issues
import os, json, datetime, calendar

@login_required()
def main(request):
    '''
    Redmine Statuses:
    Open: New, In Progress, In Test, To Be Determined, Paused
    Closed: Done, Resolved
    Rejected: Rejected, Out of Date, Not relevant, Unreproducible, Duplicate
    '''
    redmine_issues = {}
    all_issues = Redmine_issues.objects.all().order_by('-updated_on')
    redmine_issues['all_issues'] = all_issues
    redmine_issues['open_issues'] = all_issues.filter(~Q(status_name="Done") & ~Q(status_name="Resolved") & ~Q(status_name="Rejected") & ~Q(status_name="Out of date") & ~Q(status_name="Not relevant") & ~Q(status_name="Unreproducible") & ~Q(status_name="Duplicate") & ~Q(status_name="Already fixed"))
    redmine_issues['closed_issues'] = all_issues.filter(Q(status_name="Done")  | Q(status_name="Resolved"))
    redmine_issues['rejected_issues'] = all_issues.filter(Q(status_name="Rejected") | Q(status_name="Out of date") | Q(status_name="Not relevant") | Q(status_name="Unreproducible") | Q(status_name="Duplicate") | Q(status_name="Already fixed"))

    redmine_issues['all_issues_len'] = len(all_issues)
    redmine_issues['open_issues_len'] =len(redmine_issues['open_issues'])
    redmine_issues['closed_issues_len'] = len(redmine_issues['closed_issues'])
    redmine_issues['rejected_issues_len'] = len(redmine_issues['rejected_issues'])

    all_users = all_issues.values('assigned_to_name').distinct()
    redmine_issues['all_users'] = all_users
    all_status = all_issues.values('status_name').distinct()
    all_project = all_issues.values('project_name').distinct()

    #Showcase all open issues according to User, Status and Project
    #Sort them so that they are displayed from greatest to fewest
    #user_dict = {'James Fulcrumstein':0, 'Mary Littlelamb':0, 'Kent Breakfield':0, 'unassigned':0,}
    user_dict = {}
    status_dict = {}
    project_dict = {}

    for user in all_users:
        if user['assigned_to_name'] == "":
            user_dict["unassigned"] = 0
        user_dict[user['assigned_to_name']] = 0
    
    for status in all_status:
        status_dict[status['status_name']] = 0

    for project in all_project:
        project_dict[project['project_name']] = 0  

    for issue in redmine_issues['open_issues']:
        if issue.assigned_to_name in user_dict and issue.assigned_to_name != "":
            user_dict[issue.assigned_to_name] += 1
        if issue.assigned_to_name == "":
            user_dict["unassigned"] += 1
        
        if issue.status_name in status_dict:
            status_dict[issue.status_name] += 1
        
        if issue.project_name in project_dict:
            project_dict[issue.project_name] += 1

    #If a value is equal to 0, then we remove that key. 
    #No need to see which users don't have any currently assigned isues.
    #user_assigned_dict ={'James Fulcrumstein':3, 'Mary Littlelamb':5,}
    user_assigned_dict = {key:value for key, value in user_dict.items() if value != 0}
    status_assigned_dict = {key:value for key, value in status_dict.items() if value != 0}
    project_assigned_dict = {key:value for key, value in project_dict.items() if value != 0}

    #Sort the dictionary so that the the dictionary with the highest value is displayed first
    #redmine_issues['user_assigned_dict'] = [('Mary Littlelamb', 5),('James Fulcrumstein', 3)]
    redmine_issues['user_assigned_dict'] = sorted(user_assigned_dict.items(), key=lambda x: x[1], reverse=True)
    redmine_issues['status_assigned_dict'] = sorted(status_assigned_dict.items(), key=lambda x: x[1], reverse=True)
    redmine_issues['project_assigned_dict'] = sorted(project_assigned_dict.items(), key=lambda x: x[1], reverse=True)

    #Data according to the selected date
    date_request = request.GET.get('date_start')
    today, end_of_day, first_of_week, end_of_week, first_of_month, end_of_month = retrieve_dates(date_request)

    redmine_issues['date'] = {}
    redmine_issues['date']['today'] = today.strftime('%A, %B %d')
    redmine_issues['date']['end_of_day'] = end_of_day.strftime('%A, %B %d')
    redmine_issues['date']['first_of_week'] = first_of_week.strftime('%A, %B %d')
    redmine_issues['date']['end_of_week'] = end_of_week.strftime('%A, %B %d')
    redmine_issues['date']['first_of_month'] = first_of_month.strftime('%A, %B %d')
    redmine_issues['date']['end_of_month'] = end_of_month.strftime('%A, %B %d')

    redmine_issues['issues_today'] = retrieve_issue_data(redmine_issues, today, end_of_day)

    credentials_file = 'credentials.json'
    credentials_path = os.path.join(os.path.abspath('.'), credentials_file)
    with open(credentials_path) as f:
        data = f.read()
    credential_dict = json.loads(data)
    url = credential_dict['redmine_host']

    context ={
        'redmine_issues':redmine_issues,
        'url': url,
    }
    return render(request, "sales/dev.html", context) 

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


def retrieve_issue_data(redmine_issues, date_request, date_request_end):
    '''
    Returns data regards to the issues and users specified for the supplied time frame.
    '''
    #Prepare calculated data to present as a simple summary overview of the cases
    #full_cases = Cases.objects.all()
    issues_dict = {}

    issues_dict['open_issues'] = redmine_issues['all_issues'].filter(created_on__gte=date_request, created_on__lte=date_request_end)
    issues_dict['open_issues_len'] = len(issues_dict['open_issues'])

    issues_dict['updated_issues'] = redmine_issues['all_issues'].filter(updated_on__gte=date_request, updated_on__lte=date_request_end)
    issues_dict['updated_issues_len'] = len(issues_dict['updated_issues'])

    issues_dict['closed_issues'] = redmine_issues['all_issues'].filter(closed_on__gte=date_request, closed_on__lte=date_request_end)
    issues_dict['closed_issues_len'] = len(issues_dict['closed_issues'])

    try:
        issues_dict['kill_rate'] = int((issues_dict['closed_issues_len'] / issues_dict['open_issues_len']) * 100)
    except ValueError:
        issues_dict['kill_rate'] = int(0)
    except ZeroDivisionError:
        #If there are 0 opened issues and 3 closed issues, the kill rate will become 300%.
        issues_dict['kill_rate'] = int(issues_dict['closed_issues_len'] * 100)

    #We calculate how many cases were closed per user and add it to the context to be displayed
    #redmine_issues['all_users] = <QuerySet [{'assigned_username': 'James Fulcrumstein'}, {'assigned_username': 'Mary Littlelamb'}]

    #user_dict = {'James Fulcrumstein':0, 'Mary Littlelamb':0, 'Kent Breakfield':0}
    user_dict = {}
    for user in redmine_issues['all_users']:
        if user['assigned_to_name'] == "":
            user_dict["unassigned"] = 0
        user_dict[user['assigned_to_name']] = 0

    for issue in issues_dict['closed_issues']:
        if issue.assigned_to_name in user_dict and issue.assigned_to_name != "":
            user_dict[issue.assigned_to_name] += 1
        if issue.assigned_to_name == "":
            user_dict["unassigned"] += 1

    #If a value is equal to 0, then we remove that key. 
    #No need to see which users don't have any currently assigned isues.
    #user_assigned_dict ={'James Fulcrumstein':3, 'Mary Littlelamb':5,}
    user_assigned_dict = {key:value for key, value in user_dict.items() if value != 0}


    #Sort the dictionary so that the the dictionary with the highest value is displayed first
    #redmine_issues['user_assigned_dict'] = [('Mary Littlelamb', 5),('James Fulcrumstein', 3)]
    issues_dict['user_assigned_dict'] = sorted(user_assigned_dict.items(), key=lambda x: x[1], reverse=True)

    return issues_dict 

def get_all_issues(request):
    get_issues(recent=False)
    return HttpResponseRedirect("/dev")

def get_recent_issues(request):
    get_issues(recent=True)
    return HttpResponseRedirect("/dev")