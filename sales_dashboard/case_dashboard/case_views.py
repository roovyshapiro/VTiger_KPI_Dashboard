from django.shortcuts import render, HttpResponseRedirect
from .tasks import populate_db_celery_cases

def main_dashboard(request):
    print('cases!')
    return render(request, "dashboard/case_dashboard.html")

def populate_cases(request):
    populate_db_celery_cases()
    return HttpResponseRedirect("/cases")
