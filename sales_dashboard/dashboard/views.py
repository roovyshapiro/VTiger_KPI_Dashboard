from django.shortcuts import render, HttpResponseRedirect
from django.utils import timezone
from .models import Sales_stats, Phone_calls, Phone_call, Opportunities
import VTiger_Sales_API
import datetime

# Create your views here.
def home_view_bak(request):
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

def home_view(request):
    '''
    '''
    today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = today.replace(hour=23, minute = 59, second = 59, microsecond = 0)
    day = today.weekday()
    first_of_week = today + timezone.timedelta(days = -day)
    end_of_week = first_of_week + timezone.timedelta(days = 6)
    end_of_week = end_of_week.replace(hour = 23, minute = 59, second = 59)

    all_sales_opps = Opportunities.objects.all().filter(assigned_groupname='Sales')
    all_sales_calls = Phone_call.objects.all().filter(assigned_groupname='Sales')

    sales_users = Opportunities.objects.all().values('assigned_username').distinct()

    today_opps = Opportunities.objects.all().filter(modifiedtime__gte=first_of_week, modifiedtime__lte=end_of_week)

    today_phone_calls = Phone_call.objects.all().filter(modifiedtime__gte=first_of_week, modifiedtime__lte=end_of_week)

    #user_dict is the total score for both phone calls and opportunity changes
    user_dict = {}
    #user_call_dict is the total amount of phone calls only
    user_call_dict = {}
    #user_opp_dict is how many times each sales stage changed in the given time frame
    user_opp_dict = {}

    for user in sales_users:
        user_dict[user['assigned_username']] = 0
        user_call_dict[user['assigned_username']] = 0
        user_opp_dict[user['assigned_username']] = {
            'demo_scheduled_changed_at':0,
            'demo_given_changed_at':0,
            'quote_sent_changed_at':0,
            'pilot_changed_at':0,
            'needs_analysis_changed_at':0,
            'closed_lost_changed_at':0,
            'closed_won_changed_at':0,
        }


    for opp in today_opps:
        if opp.assigned_username in user_dict:
            user_dict[opp.assigned_username] += 1

        if opp.demo_scheduled_changed_at != None and opp.demo_scheduled_changed_at > first_of_week and opp.demo_scheduled_changed_at < end_of_week:
            user_opp_dict[opp.assigned_username]['demo_scheduled_changed_at'] += 1
        if opp.demo_given_changed_at != None and opp.demo_given_changed_at > first_of_week and opp.demo_given_changed_at < end_of_week:
            user_opp_dict[opp.assigned_username]['demo_given_changed_at'] += 1
        if opp.quote_sent_changed_at != None and opp.quote_sent_changed_at > first_of_week and opp.quote_sent_changed_at < end_of_week:
            user_opp_dict[opp.assigned_username]['quote_sent_changed_at'] += 1
        if opp.pilot_changed_at != None and opp.pilot_changed_at > first_of_week and opp.pilot_changed_at < end_of_week:
            user_opp_dict[opp.assigned_username]['pilot_changed_at'] += 1
        if opp.needs_analysis_changed_at != None and opp.needs_analysis_changed_at > first_of_week and opp.needs_analysis_changed_at < end_of_week:
            user_opp_dict[opp.assigned_username]['needs_analysis_changed_at'] += 1
        if opp.closed_lost_changed_at != None and opp.closed_lost_changed_at > first_of_week and opp.closed_lost_changed_at < end_of_week:
            user_opp_dict[opp.assigned_username]['closed_lost_changed_at'] += 1
        if opp.closed_won_changed_at != None and opp.closed_won_changed_at > first_of_week and opp.closed_won_changed_at < end_of_week:
            user_opp_dict[opp.assigned_username]['closed_won_changed_at'] += 1


    for call in today_phone_calls:
        if call.assigned_username in user_dict:
            user_dict[call.assigned_username] += 1
            user_call_dict[call.assigned_username] += 1

    context = {
        'user_opps':user_dict,
        'today_opps':today_opps,
    }

    print(user_dict)
    print(user_opp_dict)
    return render(request, "dashboard/dashboard.html", context) 

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
    from dashboard.tasks import get_opportunities
    get_opportunities()
    return HttpResponseRedirect('/')