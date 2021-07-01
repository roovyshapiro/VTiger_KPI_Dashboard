from django.shortcuts import render, HttpResponseRedirect
from django.utils import timezone
from django.utils.timezone import make_aware
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required


from .models import Phone_call, Opportunities
import VTiger_API
import datetime, json, os, calendar, holidays


@login_required()
def main(request):
    '''
    The primary view for the Sales Dashboard where all the calculations take place.
    Celery populates the opportunities and phone calls from today periodically.
    '''
    date_request = request.GET.get('date_start')
    if date_request == '' or date_request == None:
        today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    else:
        today = make_aware(datetime.datetime.strptime(date_request, '%Y-%m-%d'))

    end_of_day = today.replace(hour=23, minute = 59, second = 59, microsecond = 0)

    sales_data = {}

    sales_data['all_sales_opps'] = Opportunities.objects.all().filter(assigned_groupname='Sales')
    sales_data['all_sales_calls'] = Phone_call.objects.all().filter(assigned_groupname='Sales')

    sales_users_opps = sales_data['all_sales_opps'].values('assigned_username').distinct()
    sales_users_calls = sales_data['all_sales_calls'].values('assigned_username').distinct()

    #Next we create a list with all the users
    #[{'assigned_username': 'Phillibus Pickens'}, 
    # {'assigned_username': 'Frank Dinkins'}, 
    # {'assigned_username': 'Joshua Weathertree'}, 
    # {'assigned_username': 'Frank Dinkins'}, 
    # {'assigned_username': 'Joshua Weathertree'}, 
    # {'assigned_username': 'Horace Builderguild'}]
    sales_users_all  = []
    for user in sales_users_calls:
        sales_users_all.append(user) 
    for user in sales_users_opps:
        sales_users_all.append(user) 

    #Finally we create a list with distinct usernames.
    #[{'assigned_username': 'Phillibus Pickens'}, 
    # {'assigned_username': 'Frank Dinkins'}, 
    # {'assigned_username': 'Joshua Weathertree'},
    # {'assigned_username': 'Horace Builderguild'}]
    sales_data['sales_users'] = list({v['assigned_username']:v for v in sales_users_all}.values())

    today, end_of_day, first_of_week, end_of_week, week_business_days_so_far, week_business_days, first_of_month, end_of_month, month_business_days_so_far, month_business_days = retrieve_dates(date_request)

    sales_data['date'] = {}
    sales_data['date']['today'] = today.strftime('%A, %B %d')
    sales_data['date']['end_of_day'] = end_of_day.strftime('%A, %B %d')
    sales_data['date']['first_of_week'] = first_of_week.strftime('%A, %B %d')
    sales_data['date']['end_of_week'] = end_of_week.strftime('%A, %B %d')
    sales_data['date']['first_of_month'] = first_of_month.strftime('%A, %B %d')
    sales_data['date']['end_of_month'] = end_of_month.strftime('%A, %B %d')

    sales_data['business_days'] = {}
    sales_data['business_days']['week_business_days'] = week_business_days
    sales_data['business_days']['week_business_days_points'] = len(week_business_days) * 100
    sales_data['business_days']['week_business_days_so_far'] = week_business_days_so_far
    sales_data['business_days']['week_business_days_so_far_points'] = len(week_business_days_so_far) * 100

    sales_data['business_days']['month_business_days'] = month_business_days
    sales_data['business_days']['month_business_days_points'] = len(month_business_days) * 100
    sales_data['business_days']['month_business_days_so_far'] = month_business_days_so_far
    sales_data['business_days']['month_business_days_so_far_points'] = len(month_business_days_so_far) * 100

    sales_data['points_today'] = retrieve_points_data(sales_data, today, end_of_day)
    sales_data['points_week'] = retrieve_points_data(sales_data, first_of_week, end_of_week)
    sales_data['points_month'] = retrieve_points_data(sales_data, first_of_month, end_of_month)

    date_dict = {}
    #Min Max Values for Date Picker in base.html
    try:
        first_opp = sales_data['all_sales_opps'].order_by('modifiedtime').first().modifiedtime
        first_opp = first_opp.strftime('%Y-%m-%d')
        date_dict = {
            'first_db': first_opp,
            'last_db': timezone.now().strftime('%Y-%m-%d'),
            'today_date':today.strftime('%A, %B %d')
        }
    except AttributeError:
        #If there is nothing in the DB, because the project was run for the first time as example, we'll prompt the population of the db for today so the request doesn't fail
        populate_db(request)

    #The VTiger hostnames are stored in the 'credentials.json' file.
    #The URLs themselves will look something like this:
    #"host_url_calls": "https://my_vtiger_instance_name.vtiger.com/index.php?module=PhoneCalls&view=Detail&record=", 
    #"host_url_opps": "https://my_vtiger_instance_name.vtiger.com/index.php?module=Potentials&view=Detail&record="}
    credentials_file = 'credentials.json'
    credentials_path = os.path.join(os.path.abspath('.'), credentials_file)
    with open(credentials_path) as f:
        data = f.read()
    credential_dict = json.loads(data)
    urls = {}
    urls['opps_url'] = credential_dict['host_url_opps']
    urls['calls_url'] = credential_dict['host_url_calls']



    context = {
        'date_dict':date_dict,
        'urls':urls,

        'sales_data': sales_data,
    }
    return render(request, "sales/sales.html", context) 

def retrieve_points_data(sales_data, startdate, enddate):
    sales_data_time_frame = {}


    sales_data_time_frame['today_opps'] = sales_data['all_sales_opps'].filter(modifiedtime__gte=startdate, modifiedtime__lte=enddate).order_by('-modifiedtime')
    sales_data_time_frame['today_phone_calls'] = sales_data['all_sales_calls'].filter(modifiedtime__gte=startdate, modifiedtime__lte=enddate).order_by('-modifiedtime')

    #user_dict is the total score for both phone calls and opportunity stage changes
    sales_data_time_frame['user_total_score'] = {}
    #user_opp_dict is how many times each sales stage changed in the given time frame
    sales_data_time_frame['user_opp_dict'] = {}
    #User specific phone calls and opportunities
    #user_opps = {}
    #user_calls = {}
    #Dictionary with the users' last phone call/opportunity
    sales_data_time_frame['user_last_cont'] = {}

    for user in sales_data['sales_users']:
        sales_data_time_frame['user_total_score'][user['assigned_username']] = 0
        sales_data_time_frame['user_last_cont'][user['assigned_username']] = {'opp':'','call':''}
        sales_data_time_frame['user_opp_dict'][user['assigned_username']] = {
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


    for opp in sales_data_time_frame['today_opps']:
        #if opp.assigned_username in user_total_score:
        #    user_total_score[opp.assigned_username] += 1

        if opp.demo_scheduled_changed_at != None and opp.demo_scheduled_changed_at > startdate and opp.demo_scheduled_changed_at < enddate:
            sales_data_time_frame['user_opp_dict'][opp.assigned_username]['Demo Scheduled'] += 1
            sales_data_time_frame['user_total_score'][opp.assigned_username] += 5
        if opp.demo_given_changed_at != None and opp.demo_given_changed_at > startdate and opp.demo_given_changed_at < enddate:
            sales_data_time_frame['user_opp_dict'][opp.assigned_username]['Demo Given'] += 1
            sales_data_time_frame['user_total_score'][opp.assigned_username] += 10
        if opp.quote_sent_changed_at != None and opp.quote_sent_changed_at > startdate and opp.quote_sent_changed_at < enddate:
            sales_data_time_frame['user_opp_dict'][opp.assigned_username]['Quote Sent'] += 1
        if opp.pilot_changed_at != None and opp.pilot_changed_at > startdate and opp.pilot_changed_at < enddate:
            sales_data_time_frame['user_opp_dict'][opp.assigned_username]['Pilot'] += 1
        if opp.needs_analysis_changed_at != None and opp.needs_analysis_changed_at > startdate and opp.needs_analysis_changed_at < enddate:
            sales_data_time_frame['user_opp_dict'][opp.assigned_username]['Needs Analysis'] += 1
        if opp.closed_won_changed_at != None and opp.closed_won_changed_at > startdate and opp.closed_won_changed_at < enddate:
            sales_data_time_frame['user_opp_dict'][opp.assigned_username]['Closed Won'] += 1
        if opp.closed_lost_changed_at != None and opp.closed_lost_changed_at > startdate and opp.closed_lost_changed_at < enddate:
            sales_data_time_frame['user_opp_dict'][opp.assigned_username]['Closed Lost'] += 1


    for call in sales_data_time_frame['today_phone_calls']:
        if call.assigned_username in sales_data_time_frame['user_total_score']:
            sales_data_time_frame['user_total_score'][call.assigned_username] += 1
            sales_data_time_frame['user_opp_dict'][call.assigned_username]['Phone Calls'] += 1
    
    #We find the most recent phone call and opportunity modified for each user
    #If their score is zero for the day, then the time of their most recent contribution is displayed
    #(After seven days of no contributions, we no longer display that user)
    for k in sales_data_time_frame['user_total_score']:
        last_opp = sales_data['all_sales_opps'].filter(assigned_username=k).order_by('modifiedtime').last()
        last_call = sales_data['all_sales_calls'].filter(assigned_username=k).order_by('modifiedtime').last()
        try:
            sales_data_time_frame['user_last_cont'][k]['opp'] = last_opp.modifiedtime
        except AttributeError:
            #This user doesn't have any modified opportunities
            sales_data_time_frame['user_last_cont'][k]['opp'] = 'never'
        try:
            sales_data_time_frame['user_last_cont'][k]['call'] = last_call.modifiedtime
        except AttributeError:
            #This user didn't make any phone calls
            sales_data_time_frame['user_last_cont'][k]['call'] = 'never'
    for k,v in sales_data_time_frame['user_total_score'].items():
        if v != 0:
            del(sales_data_time_frame['user_last_cont'][k])

    #If a user has 0 points for that given time frame, they are not displayed.
    for user in sales_data['sales_users']:
        if sales_data_time_frame['user_total_score'][user['assigned_username']] == 0:
            del(sales_data_time_frame['user_total_score'][user['assigned_username']])
            del(sales_data_time_frame['user_opp_dict'][user['assigned_username']])

    return sales_data_time_frame

def retrieve_dates(date_request):
    '''
    today = (datetime.datetime(2020, 12, 4, 0, 0) 
    end_of_day = (datetime.datetime(2020, 12, 4, 23, 59) 

    first_of_week = (datetime.datetime(2020, 11, 30, 0, 0) 
    end_of_week = (datetime.datetime(2020, 12, 6, 23, 59) 

    first_of_month = (datetime.datetime(2020, 12, 1, 0, 0)
    end_of_month = (datetime.datetime(2020, 12, 31, 23, 59)
    '''
    if date_request == '' or date_request == None:
        today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    else:
        today = make_aware(datetime.datetime.strptime(date_request, '%Y-%m-%d'))

    end_of_day = today.replace(hour=23, minute = 59, second = 59, microsecond = 0)

    #0 = monday, 5 = Saturday, 6 = Sunday 
    day = today.weekday()
    first_of_week = today + timezone.timedelta(days = -day)
    end_of_week = first_of_week + timezone.timedelta(days = 6)
    end_of_week = end_of_week.replace(hour = 23, minute = 59, second = 59)
    week_business_days_so_far, week_business_days = calculate_business_days(today, first_of_week, end_of_week)

    first_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    year = first_of_month.year
    month = first_of_month.month
    last_day = calendar.monthrange(year,month)[1]
    end_of_month = first_of_month.replace(day=last_day, hour=23, minute=59, second=59)
    month_business_days_so_far, month_business_days = calculate_business_days(today, first_of_month, end_of_month)

    return today, end_of_day, first_of_week, end_of_week, week_business_days_so_far, week_business_days, first_of_month, end_of_month, month_business_days_so_far, month_business_days

def calculate_business_days(today, startdate, enddate):
    '''
    In order to calculate a salesperson's average points per day in a month's timeframe,
    We need to know how many business days are in that month.
    You can't do 100 * 30 because months have variable days.
    Weekends and holidays must be taken into account as well.
    Once we know exactly how many working days are in a month (and week) we can then
    multiply that number by 100 and set a goal for the salesperson to reach an average
    of 100 points per day over that timeframe.
    The Holidays packace is used to determine holidays for a given timeframe.
    Create a new list with all the current year's holidays
    (datetime.date(2021, 1, 1), "New Year's Day")
    (datetime.date(2021, 12, 31), "New Year's Day (Observed)")
    (datetime.date(2021, 1, 18), 'Martin Luther King Jr. Day')
    (datetime.date(2021, 2, 15), "Washington's Birthday")
    (datetime.date(2021, 5, 31), 'Memorial Day')
    (datetime.date(2021, 7, 4), 'Independence Day')
    (datetime.date(2021, 7, 5), 'Independence Day (Observed)')
    (datetime.date(2021, 9, 6), 'Labor Day')
    (datetime.date(2021, 10, 11), 'Columbus Day')
    (datetime.date(2021, 11, 11), 'Veterans Day')
    (datetime.date(2021, 11, 25), 'Thanksgiving')
    (datetime.date(2021, 12, 25), 'Christmas Day')
    (datetime.date(2021, 12, 24), 'Christmas Day (Observed)') 

    Since it returns a tuple with the datetime date and the name of the holiday,
    only the datetime is saved.
    year = startdate.year
    holiday_list = []
    for holiday in holidays.UnitedStates(years=year).items():
	    holiday_list.append(holiday[0])
    '''

    #range is exclusive
    number_of_days = (enddate - startdate).days + 1

    #Get a list of all the dates in this timeframe
    all_dates = [startdate + datetime.timedelta(days=x) for x in range(number_of_days)]
    #We also retrieve how many non-weekend/holiday dates have past thus far in the selected date
    number_of_days_so_far = (today - startdate).days + 1
    all_dates_so_far = [startdate + datetime.timedelta(days=x) for x in range(number_of_days_so_far)]

    #Remove times with "date()"
    all_dates = [d.date() for d in all_dates]
    all_dates_so_far = [d.date() for d in all_dates_so_far]

    #See docstring for more info
    year = startdate.year
    holiday_list = []
    for holiday in holidays.UnitedStates(years=year).items():
	    holiday_list.append(holiday[0])
    #Creates new list which excludes all dates if the date falls on a holiday
    dates_no_holiday = [d for d in all_dates if d not in holiday_list]
    dates_no_holiday_so_far = [d for d in all_dates_so_far if d not in holiday_list]

    #create a new list which excludes all dates if the date falls on a weekend
    no_weekend_holiday_date_list = [d for d in dates_no_holiday if not d.isoweekday() in [6,7]]
    no_weekend_holiday_date_list_so_far = [d for d in dates_no_holiday_so_far if not d.isoweekday() in [6,7]]

    return no_weekend_holiday_date_list_so_far, no_weekend_holiday_date_list


@login_required()
@staff_member_required
def populate_db(request):
    '''
    Populates the opportunities and phone calls databases.
    '''
    from sales.tasks import get_opportunities
    get_opportunities()

    from sales.tasks import get_phonecalls
    get_phonecalls()

    return HttpResponseRedirect('/sales')

@login_required()
@staff_member_required
def populate_opp_month(request):
    '''
    Populates the opportunities and phone calls databases from the past 3 months.
    '''
    from sales.tasks import get_opportunities
    get_opportunities(day='month')

    return HttpResponseRedirect('/sales')

@login_required()
@staff_member_required
def populate_call_month(request):
    '''
    Populates the opportunities and phone calls databases from the past 3 months.
    '''
    from sales.tasks import get_phonecalls
    get_phonecalls(day='month')

    return HttpResponseRedirect('/sales')

@login_required()
@staff_member_required
def delete_all_items(request):
    '''
    Delete all the items in the database from today only.
    Convenient to reset the day's data without deleting previous days' data.
    '''
    today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = timezone.now().replace(hour=23, minute=59, second=59, microsecond=0)
    today_opps = Opportunities.objects.all().filter(date_modified__gte=today_start, date_modified__lte=today_end)
    today_calls = Phone_call.objects.all().filter(date_modified__gte=today_start, date_modified__lte=today_end)

    today_opps.delete()
    today_calls.delete()

    #This deletes all items:
    #today_opps.objects.all().delete()
    #today_calls.objects.all().delete()
    return HttpResponseRedirect('/sales')

@login_required()
@staff_member_required
def test_method(request):
    '''
    localhost:8000/test
    Useful for testing functionality
    '''
    print('test!')
    return HttpResponseRedirect('/sales')