from django.shortcuts import render, HttpResponseRedirect
from django.http import HttpResponse
from django.db.models import Q
from django.utils import timezone
from django.contrib.auth.decorators import login_required
import os, json, datetime, calendar

@login_required()
def main(request):
    '''
    '''
    context = {
        
    }
    return render(request, "sales/docs.html", context) 