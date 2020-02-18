from django.shortcuts import render, HttpResponseRedirect

from .models import Sales_stats, Phone_calls
import VTiger_Sales_API

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
    except TypeError:
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
    populate_db_celery()
    return HttpResponseRedirect('/')

def delete_all_items(request):
    '''
    Delete all the items in the database.
    This is useful for testing but will probably not make it to the final version.
    '''
    Sales_stats.objects.all().delete()
    Phone_calls.objects.all().delete()
    return HttpResponseRedirect('/')

def test_method(request):
    '''
    localhost:8000/test
    Useful for testing functionality
    '''
    from dashboard.tasks import populate_db_celery
    populate_db_celery.delay()
    return HttpResponseRedirect('/')