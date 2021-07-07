from django.shortcuts import render, HttpResponseRedirect
from django.http import HttpResponse
from django.utils import timezone
from django.utils.timezone import make_aware
from django.contrib.auth.decorators import login_required


#import datetime, json, os, calendar, holidays

@login_required()
def main(request, user):
    '''
    Useful for testing functionality
    '''
    print(user)
    return HttpResponse(f"You selected {user}")
