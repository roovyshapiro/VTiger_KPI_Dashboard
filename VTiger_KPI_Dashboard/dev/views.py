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
    redmine_issues['open_issues'] = all_issues.filter(~Q(status_name="Done") & ~Q(status_name="Resolved") & ~Q(status_name="Rejected") & ~Q(status_name="Out of date") & ~Q(status_name="Not relevant") & ~Q(status_name="Unreproducible") & ~Q(status_name="Duplicate"))
    redmine_issues['closed_issues'] = all_issues.filter(Q(status_name="Done")  | Q(status_name="Resolved"))
    redmine_issues['rejected_issues'] = all_issues.filter(Q(status_name="Rejected") | Q(status_name="Out of date") | Q(status_name="Not relevant") | Q(status_name="Unreproducible") | Q(status_name="Duplicate"))

    redmine_issues['all_issues_len'] = len(all_issues)
    redmine_issues['open_issues_len'] =len(redmine_issues['open_issues'])
    redmine_issues['closed_issues_len'] = len(redmine_issues['closed_issues'])
    redmine_issues['rejected_issues_len'] = len(redmine_issues['rejected_issues'])

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