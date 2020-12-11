from django.shortcuts import render, HttpResponseRedirect
from django.utils import timezone
from .models import Sales_stats, Phone_calls, Phone_call, Opportunities
import VTiger_Sales_API
import datetime

def home_view(request):
    '''
    The primary view for the Sales Dashboard where all the calculations take place.
    Celery populates the opportunities and phone calls from today periodically.
    '''
    today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = today.replace(hour=23, minute = 59, second = 59, microsecond = 0)
    day = today.weekday()
    first_of_week = today + timezone.timedelta(days = -day)
    end_of_week = first_of_week + timezone.timedelta(days = 6)
    end_of_week = end_of_week.replace(hour = 23, minute = 59, second = 59)

    all_sales_opps = Opportunities.objects.all().filter(assigned_groupname='Sales')
    all_sales_calls = Phone_call.objects.all().filter(assigned_groupname='Sales')

    sales_users = all_sales_opps.values('assigned_username').distinct()

    today_opps = all_sales_opps.filter(modifiedtime__gte=today, modifiedtime__lte=end_of_day).order_by('-modifiedtime')
    today_phone_calls = all_sales_calls.filter(modifiedtime__gte=today, modifiedtime__lte=end_of_day).order_by('-modifiedtime')

    #user_dict is the total score for both phone calls and opportunity stage changes
    user_total_score = {}
    #user_opp_dict is how many times each sales stage changed in the given time frame
    user_opp_dict = {}
    #User specific phone calls and opportunities
    user_opps = {}
    user_calls = {}

    for user in sales_users:
        user_total_score[user['assigned_username']] = 0
        user_opp_dict[user['assigned_username']] = {
            'Demo Scheduled':0,
            'Demo Given':0,
            'Quote Sent':0,
            'Pilot':0,
            'Needs Analysis':0,
            'Closed Won':0,
            'Closed Lost':0,
            'Phone Calls':0,
        }
        #If we want to display opp and phone call data per user
        #user_opps[user['assigned_username']] = today_opps.filter(assigned_username=user['assigned_username'])
        #user_calls[user['assigned_username']] = today_phone_calls.filter(assigned_username=user['assigned_username'])


    for opp in today_opps:
        #if opp.assigned_username in user_total_score:
        #    user_total_score[opp.assigned_username] += 1

        if opp.demo_scheduled_changed_at != None and opp.demo_scheduled_changed_at > today and opp.demo_scheduled_changed_at < end_of_day:
            user_opp_dict[opp.assigned_username]['Demo Scheduled'] += 1
            user_total_score[opp.assigned_username] += 5
        if opp.demo_given_changed_at != None and opp.demo_given_changed_at > today and opp.demo_given_changed_at < end_of_day:
            user_opp_dict[opp.assigned_username]['Demo Given'] += 1
            user_total_score[opp.assigned_username] += 10
        if opp.quote_sent_changed_at != None and opp.quote_sent_changed_at > today and opp.quote_sent_changed_at < end_of_day:
            user_opp_dict[opp.assigned_username]['Quote Sent'] += 1
        if opp.pilot_changed_at != None and opp.pilot_changed_at > today and opp.pilot_changed_at < end_of_day:
            user_opp_dict[opp.assigned_username]['Pilot'] += 1
        if opp.needs_analysis_changed_at != None and opp.needs_analysis_changed_at > today and opp.needs_analysis_changed_at < end_of_day:
            user_opp_dict[opp.assigned_username]['Needs Analysis'] += 1
        if opp.closed_won_changed_at != None and opp.closed_won_changed_at > today and opp.closed_won_changed_at < end_of_day:
            user_opp_dict[opp.assigned_username]['Closed Won'] += 1
        if opp.closed_lost_changed_at != None and opp.closed_lost_changed_at > today and opp.closed_lost_changed_at < end_of_day:
            user_opp_dict[opp.assigned_username]['Closed Lost'] += 1

    for call in today_phone_calls:
        if call.assigned_username in user_total_score:
            user_total_score[call.assigned_username] += 1
            user_opp_dict[call.assigned_username]['Phone Calls'] += 1

    context = {
        'user_total_score':user_total_score,
        'user_opp_dict': user_opp_dict,
        'user_opps':user_opps,
        'user_calls':user_calls,
        'today_opps':today_opps,
        'today_phone_calls':today_phone_calls,
    }

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
    #from dashboard.tasks import get_opportunities
    #get_opportunities()

    from dashboard.tasks import get_phonecalls
    get_phonecalls()

    return HttpResponseRedirect('/')