from django.shortcuts import render, HttpResponseRedirect
from django.http import HttpResponse
from django.db.models import Q
from .tasks import get_issues
from .models import Redmine_issues
import os, json

def main(request):
    all_issues = Redmine_issues.objects.all().order_by('-updated_on')
    open_issues = all_issues.filter(~Q(status_name="Done"))
    closed_issues = all_issues.filter(Q(status_name="Done"))

    credentials_file = 'credentials.json'
    credentials_path = os.path.join(os.path.abspath('.'), credentials_file)
    with open(credentials_path) as f:
        data = f.read()
    credential_dict = json.loads(data)
    url = credential_dict['redmine_host']

    context ={
        'all_issues':all_issues,
        'open_issues':open_issues,
        'closed_issues':closed_issues,
        'url': url,
    }
    return render(request, "sales/dev.html", context) 

def get_all_issues(request):
    get_issues(recent=False)
    return HttpResponseRedirect("/dev")

def get_recent_issues(request):
    get_issues(recent=True)
    return HttpResponseRedirect("/dev")