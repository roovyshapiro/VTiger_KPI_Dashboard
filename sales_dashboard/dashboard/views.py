from django.shortcuts import render, HttpResponseRedirect
from django.utils import timezone
from .models import Sales_stats, Phone_calls
import VTiger_Sales_API
import datetime

# Create your views here.
def home_view(request):
    '''
    Loads the main page. 
    If there is no data in the database, then the populate url is called
    Which automatically pulls data from the database.
    '''
    try:
        sales_stats = Sales_stats
        stats = sales_stats.objects.all()
        user_stat_dict, user_score_dict = sales_stats.user_totals()

        return render(request, 'dashboard/dashboard.html', {'stats':stats, 'stat_total':user_stat_dict, 'score_total':user_score_dict,})
    #If the database is empty, then an IndexError will be generated from models.user_totals()
    #Because the database queries return no results.
    except (IndexError):
        return HttpResponseRedirect('/populate/')

def populate_db(request):
    '''
    Populates the database with stats from vtigerapi.db_update()
    This function is run on a schedule by Celery but it can be run manually by navigating
    to localhost:8000/populate for testing.
    demo_scheduled, demo_given, quote_sent, pilot, needs_analysis, closed_won, closed_lost, phone_calls, date, user
    {james_frinkle:[0, 1, 15, 0, 0, 3, 6, '215', '2020-01-28 21:30:00', 'james_frinkle']}
    '''
    from .tasks import populate_db_celery
    populate_db_celery.delay()
    return HttpResponseRedirect('/')

def delete_all_items(request):
    '''
    Delete all the items in the database from today only.
    Convenient to reset the day's data without deleting previous days' data.
    '''
    from django.utils import timezone
    today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = timezone.now().replace(hour=23, minute=59, second=59, microsecond=0)
    stat_results = Sales_stats.objects.all().filter(date_modified__gte=today_start, date_modified__lte=today_end)
    phone_results = Phone_calls.objects.all().filter(date_modified__gte=today_start, date_modified__lte=today_end)

    stat_results.delete()
    phone_results.delete()

    #This deletes all items:
    #Sales_stats.objects.all().delete()
    #Phone_calls.objects.all().delete()
    return HttpResponseRedirect('/')

def test_method(request):
    '''
    localhost:8000/test
    Useful for testing functionality
    '''
    from dashboard.tasks import get_phonecalls
    get_phonecalls()
    return HttpResponseRedirect('/')