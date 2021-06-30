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
    redmine_issues['all_issues_created_ordered'] = all_issues.order_by('-created_on')
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

    #Showissue all open issues according to User, Status and Project
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
    redmine_issues['issues_week'] = retrieve_issue_data(redmine_issues, first_of_week, end_of_week)
    redmine_issues['issues_month'] = retrieve_issue_data(redmine_issues, first_of_month, end_of_month)

    #We supply dictionaries of all the created issues to the html context so that we can easily pinpoint issues that were
    #created in that time frame. We highlight created issues in green and resolved issues in red.
    redmine_issues['open_issues_dict_day'] = {}
    for issue in redmine_issues['issues_today']['open_issues']:
        redmine_issues['open_issues_dict_day'][issue.issue_id] = issue.issue_id

    redmine_issues['open_issues_dict_week'] = {}
    for issue in redmine_issues['issues_week']['open_issues']:
        redmine_issues['open_issues_dict_week'][issue.issue_id] = issue.issue_id

    redmine_issues['open_issues_dict_month'] = {}
    for issue in redmine_issues['issues_month']['open_issues']:
        redmine_issues['open_issues_dict_month'][issue.issue_id] = issue.issue_id

    #We supply dictionaries of all the resolved issues to the html context so that we can easily pinpoint issues that were
    #resolved in that time frame. We highlight created issues in green and resolved issues in red.
    redmine_issues['resolved_issues_dict_day'] = {}
    for issue in redmine_issues['issues_today']['closed_issues']:
        redmine_issues['resolved_issues_dict_day'][issue.issue_id] = issue.issue_id

    redmine_issues['resolved_issues_dict_week'] = {}
    for issue in redmine_issues['issues_week']['closed_issues']:
        redmine_issues['resolved_issues_dict_week'][issue.issue_id] = issue.issue_id

    redmine_issues['resolved_issues_dict_month'] = {}
    for issue in redmine_issues['issues_month']['closed_issues']:
        redmine_issues['resolved_issues_dict_month'][issue.issue_id] = issue.issue_id

    redmine_issues['historical_data'] = retrieve_historical_data(redmine_issues['all_issues_created_ordered'])
    redmine_issues['month_comparison_resolved'] = month_comparison_data(redmine_issues['all_issues'], issue_status="resolved")
    redmine_issues['month_comparison_created'] = month_comparison_data(redmine_issues['all_issues'], issue_status="created")

    credentials_file = 'credentials.json'
    credentials_path = os.path.join(os.path.abspath('.'), credentials_file)
    with open(credentials_path) as f:
        data = f.read()
    credential_dict = json.loads(data)
    url = credential_dict['redmine_host']

    #Min Max Values for Date Picker in base.html
    date_dict = {}
    first_issue = redmine_issues['all_issues'].order_by('created_on').first().created_on
    first_issue = first_issue.strftime('%Y-%m-%d')
    date_dict = {
        'first_db': first_issue,
        'last_db': timezone.now().strftime('%Y-%m-%d'),
    }

    context ={
        'redmine_issues':redmine_issues,
        'url': url,
        'date_dict':date_dict,
    }

    #If today is monday, and the user chooses to look at today's data, then the week's data will not
    #be shown. That is because if the current day is Monday, it will always be identical to the week's
    #data as no other data for days beyond today exist. 
    #However, if we look at a Monday in the past, then the data for the week will be different.
    #In addition, the week data also won't be shown if the week and month data is the same.
    #This occurs if the beginning of the week and the beginning of the month coincide
    if (today.weekday() == 0 and today.strftime('%Y-%m-%d') == timezone.now().strftime('%Y-%m-%d')) or (len(redmine_issues['issues_week']['all_issues']) == len(redmine_issues['issues_month']['all_issues'])):
        del redmine_issues['issues_week']

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
    #Prepare calculated data to present as a simple summary overview of the issues
    #full_issues = Cases.objects.all()
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

    #We calculate how many issues were closed per user and add it to the context to be displayed
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

    issues_dict['all_issues'] = issues_dict['open_issues'] | issues_dict['updated_issues'] | issues_dict['closed_issues']

    return issues_dict 

def retrieve_historical_data(all_issues):
    '''
    First, we go through all issues and find all the unique years based on created time.
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
    created, resolved, kill rates,
    {
        1: {
            'first_of_month': datetime.datetime(2021, 1, 1, 0, 0, tzinfo=<UTC>), 
            'end_of_month': datetime.datetime(2021, 1, 31, 23, 59, 59, tzinfo=<UTC>), 
            'month': 'January', 
            'year': 2021, 
            'created_all': 282, 
            'resolved_all': 252
            }, 
        2: {
            'first_of_month': datetime.datetime(2021, 2, 1, 0, 0, tzinfo=<UTC>), 
            'end_of_month': datetime.datetime(2021, 2, 28, 23, 59, 59, tzinfo=<UTC>), 
            'month': 'February', 
            'year': 2021, 
            'created_all': 253, 
            'resolved_all': 212
            },
    }
    '''
    #Only show data for the past two years
    #Otherwise, there's too many months and the chart gets clogged
    thisyear = all_issues.first().created_on.year
    two_years_ago = all_issues.first().created_on.replace(year=thisyear - 2, month=1, day = 1, hour =0, minute = 0)
    full_issues = all_issues.filter(created_on__gte=two_years_ago)
    #get a list of all unique years which are used in issues
    issue_years = []
    for issue in full_issues:
        year = issue.created_on.year
        if year not in issue_years:
            issue_years.append(year)

    all_data = {}
    for year in issue_years:
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
            created_issues = full_issues.filter(created_on__gte=first_of_month, created_on__lte=end_of_month)
            months[i]['created_all'] = len(created_issues)
            resolved_issues = full_issues.filter(closed_on__gte=first_of_month, closed_on__lte=end_of_month)
            months[i]['resolved_all'] = len(resolved_issues)
        
            try:
                months[i]['kill_rate_all'] = int((months[i]['resolved_all'] / months[i]['created_all']) * 100)
            except ValueError:
                months[i]['kill_rate_all'] = int(0)
            except ZeroDivisionError:
                #If there are 0 opened issues and 3 closed issues, the kill rate will become 300%.
                months[i]['kill_rate_all'] = int(months[i]['resolved_all'] * 100)


    #Ultimately, we only want to display data that exists and not empty data for all future and past months
    #A new dict is created which only contains non-empty month data inside
    all_dict_non_empty = {i:{} for i in all_data}
    for year, months in all_data.items():
        for month, month_dict in months.items():
            if month_dict['created_all'] != 0 and month_dict['resolved_all'] != 0:
                all_dict_non_empty[year][month] = month_dict
    return all_dict_non_empty

def month_comparison_data(all_issues, issue_status):
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
        date_range = [comparison_data[month]['first_day'] + datetime.timedelta(days=x) for x in range(0, (comparison_data[month]['last_day'] - comparison_data[month]['first_day']).days + 1)]
        for date in date_range:
            date_count = 0
            if issue_status == "resolved":
                for issue in all_issues.filter(closed_on__gte=comparison_data[month]['first_day'], closed_on__lte=comparison_data[month]['last_day']):
                    if issue.closed_on.replace(hour=0, minute = 0, second=0,microsecond=0) == date:
                        date_count += 1
                comparison_data[month]['resolved'].append(date_count)
            elif issue_status == "created":
                for issue in all_issues.filter(created_on__gte=comparison_data[month]['first_day'], created_on__lte=comparison_data[month]['last_day']):
                    if issue.created_on.replace(hour=0, minute = 0, second=0,microsecond=0) == date:
                        date_count += 1
                comparison_data[month]['created'].append(date_count)
    print(comparison_data)
    return comparison_data

def get_all_issues(request):
    get_issues(recent=False)
    return HttpResponseRedirect("/dev")

def get_recent_issues(request):
    get_issues(recent=True)
    return HttpResponseRedirect("/dev")