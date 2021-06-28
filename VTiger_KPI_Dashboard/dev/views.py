from django.shortcuts import render, HttpResponseRedirect
from django.http import HttpResponse
from django.db.models import Q
from .tasks import get_issues
from .models import Redmine_issues
import os, json

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

def get_all_issues(request):
    get_issues(recent=False)
    return HttpResponseRedirect("/dev")

def get_recent_issues(request):
    get_issues(recent=True)
    return HttpResponseRedirect("/dev")