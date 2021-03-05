from django.shortcuts import render, HttpResponseRedirect
from django.utils import timezone
from django.utils.timezone import make_aware
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required


from .models import Phone_call, Opportunities
import VTiger_API
import datetime, json, os


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

    all_sales_opps = Opportunities.objects.all().filter(assigned_groupname='Sales')
    all_sales_calls = Phone_call.objects.all().filter(assigned_groupname='Sales')

    #Only display users who have either modified an opportunity or made a phone call within the past 7 days.
    #There could be a sales person whose last phone call was one year ago. We wouldn't want that user's data to be continually
    #displayed with 0 points
    seven_days_ago = today + timezone.timedelta(days = -7)
    seven_days_ago_opps = all_sales_opps.filter(modifiedtime__gte=seven_days_ago,  modifiedtime__lte=end_of_day).order_by('-modifiedtime')
    seven_days_ago_calls = all_sales_calls.filter(modifiedtime__gte=seven_days_ago,  modifiedtime__lte=end_of_day).order_by('-modifiedtime')

    #In order to get all the sales users who've made contributions within the past 7 days, 
    #we get distinct "assigned_usernames" from both the opportunities and phone call DBs.
    #This will get us all the users but as you can see there may be duplicates.
    #<QuerySet [{'assigned_username': 'Frank Dinkins'}, {'assigned_username': 'Joshua Weathertree'}, {'assigned_username': 'Horace Builderguild'}]>
    #<QuerySet [{'assigned_username': 'Phillibus Pickens'}, {'assigned_username': 'Frank Dinkins'}, {'assigned_username': 'Joshua Weathertree'}]>
    sales_users_opps = seven_days_ago_opps.values('assigned_username').distinct()
    sales_users_calls = seven_days_ago_calls.values('assigned_username').distinct()

    #Next we create a list with all the users
    #[{'assigned_username': 'Phillibus Pickens'}, 
    # {'assigned_username': 'Frank Dinkins'}, 
    # {'assigned_username': 'Joshua Weathertree'}, 
    # {'assigned_username': 'Frank Dinkins'}, 
    # {'assigned_username': 'Joshua Weathertree'}, 
    # {'assigned_username': 'Horace Builderguild'}]
    sales_users_all = []
    for user in sales_users_calls:
        sales_users_all.append(user) 
    for user in sales_users_opps:
        sales_users_all.append(user) 

    #Finally we create a list with distinct usernames.
    #[{'assigned_username': 'Phillibus Pickens'}, 
    # {'assigned_username': 'Frank Dinkins'}, 
    # {'assigned_username': 'Joshua Weathertree'},
    # {'assigned_username': 'Horace Builderguild'}]
    sales_users = list({v['assigned_username']:v for v in sales_users_all}.values())

    today_opps = all_sales_opps.filter(modifiedtime__gte=today, modifiedtime__lte=end_of_day).order_by('-modifiedtime')
    today_phone_calls = all_sales_calls.filter(modifiedtime__gte=today, modifiedtime__lte=end_of_day).order_by('-modifiedtime')

    #user_dict is the total score for both phone calls and opportunity stage changes
    user_total_score = {}
    #user_opp_dict is how many times each sales stage changed in the given time frame
    user_opp_dict = {}
    #User specific phone calls and opportunities
    user_opps = {}
    user_calls = {}
    #Dictionary with the users' last phone call/opportunity
    user_last_cont = {}

    for user in sales_users:
        user_total_score[user['assigned_username']] = 0
        user_last_cont[user['assigned_username']] = {'opp':'','call':''}
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

    #We find the most recent phone call and opportunity modified for each user
    #If their score is zero for the day, then the time of their most recent contribution is displayed
    #(After seven days of no contributions, we no longer display that user)
    before_today_opps = Opportunities.objects.all().filter(modifiedtime__lte=end_of_day)
    before_today_calls = Phone_call.objects.all().filter(modifiedtime__lte=end_of_day)
        
    for k in user_total_score:
        last_opp = before_today_opps.filter(assigned_username=k).order_by('modifiedtime').last()
        last_call = before_today_calls.filter(assigned_username=k).order_by('modifiedtime').last()
        try:
            user_last_cont[k]['opp'] = last_opp.modifiedtime
        except AttributeError:
            #This user doesn't have any modified opportunities
            user_last_cont[k]['opp'] = 'never'
        try:
            user_last_cont[k]['call'] = last_call.modifiedtime
        except AttributeError:
            #This user didn't make any phone calls
            user_last_cont[k]['call'] = 'never'
    for k,v in user_total_score.items():
        if v != 0:
            del(user_last_cont[k])

    date_dict = {}
    #Min Max Values for Date Picker in base.html
    try:
        first_opp = all_sales_opps.order_by('modifiedtime').first().modifiedtime
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
        'user_total_score':user_total_score,
        'user_opp_dict': user_opp_dict,
        'user_opps':user_opps,
        'user_calls':user_calls,
        'today_opps':today_opps,
        'today_phone_calls':today_phone_calls,
        'date_dict':date_dict,
        'urls':urls,
        'user_last_cont':user_last_cont,
    }
    return render(request, "sales/sales.html", context) 

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