from django.shortcuts import render, HttpResponseRedirect
from django.utils import timezone

from .tasks import populate_db_celery_cases
from .models import Cases

def main_dashboard(request):
    print('cases!')
    return render(request, "dashboard/case_dashboard.html")

def populate_cases(request):
    populate_db_celery_cases()
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