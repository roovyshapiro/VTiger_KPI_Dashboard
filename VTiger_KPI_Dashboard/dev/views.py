from django.shortcuts import render, HttpResponseRedirect
from django.http import HttpResponse
from .tasks import get_issues

def main(request):
    return HttpResponse("Future site of the Dev Dashboard!")

def get_all_issues(request):
    get_issues(recent=False)
    return HttpResponseRedirect("/dev")

def get_recent_issues(request):
    get_issues(recent=True)
    return HttpResponseRedirect("/dev")