from django.shortcuts import render, HttpResponseRedirect
from django.http import HttpResponse
from django.db.models import Q
from django.utils import timezone
from django.contrib.auth.decorators import login_required
import os, json, datetime, calendar
from .models import Docs
from .tasks import get_docs


@login_required()
def main(request):
    '''
    '''

    docs = {}
    docs['all_docs'] = Docs.objects.all().order_by('-updated_at')

    docs['all_users'] = docs['all_docs'].values('updated_by_name').distinct()

    #Data according to the selected date
    date_request = request.GET.get('date_start')
    today, end_of_day, first_of_week, end_of_week, first_of_month, end_of_month = retrieve_dates(date_request)

    docs['date'] = {}
    docs['date']['today'] = today.strftime('%A, %B %d')
    docs['date']['end_of_day'] = end_of_day.strftime('%A, %B %d')
    docs['date']['first_of_week'] = first_of_week.strftime('%A, %B %d')
    docs['date']['end_of_week'] = end_of_week.strftime('%A, %B %d')
    docs['date']['first_of_month'] = first_of_month.strftime('%A, %B %d')
    docs['date']['end_of_month'] = end_of_month.strftime('%A, %B %d')

    docs['docs_today'] = retrieve_doc_data(docs, today, end_of_day)
    docs['docs_week'] = retrieve_doc_data(docs, first_of_week, end_of_week)
    docs['docs_month'] = retrieve_doc_data(docs, first_of_month, end_of_month)

    #Min Max Values for Date Picker in base.html
    date_dict = {}
    first_doc = docs['all_docs'].order_by('created_at').first().updated_at
    first_doc = first_doc.strftime('%Y-%m-%d')
    date_dict = {
        'first_db': first_doc,
        'last_db': timezone.now().strftime('%Y-%m-%d'),
    }

    credentials_file = 'credentials.json'
    credentials_path = os.path.join(os.path.abspath('.'), credentials_file)
    with open(credentials_path) as f:
        data = f.read()
    credential_dict = json.loads(data)
    url = credential_dict['docs_url']

    context = {
        'docs':docs,
        'url':url,
        'date_dict':date_dict,
    }
    return render(request, "sales/docs.html", context) 

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
        today = datetime.datetime.strptime(date_request, '%Y-%m-%d')

    end_of_day = today.replace(hour=23, minute = 59, second = 59, microsecond = 0)

    #0 = monday, 5 = Saturday, 6 = Sunday 
    day = today.weekday()
    first_of_week = today + timezone.timedelta(days = -day)
    end_of_week = first_of_week + timezone.timedelta(days = 6)
    end_of_week = end_of_week.replace(hour = 23, minute = 59, second = 59)

    first_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    year = first_of_month.year
    month = first_of_month.month
    last_day = calendar.monthrange(year,month)[1]
    end_of_month = first_of_month.replace(day=last_day, hour=23, minute=59, second=59)

    return today, end_of_day, first_of_week, end_of_week, first_of_month, end_of_month


def retrieve_doc_data(docs, date_request, date_request_end):
    '''
    Returns data regards to the docs and users specified for the supplied time frame.
    '''
    #Prepare calculated data to present as a simple summary overview of the docs
    #full_docs = Cases.objects.all()
    docs_dict = {}

    docs_dict['updated_docs'] = docs['all_docs'].filter(updated_at__gte=date_request, updated_at__lte=date_request_end)
    docs_dict['updated_docs_len'] = len(docs_dict['updated_docs'])


    #We calculate how many docs were updated per user and add it to the context to be displayed
    #docs['all_users] = <QuerySet [{'assigned_username': 'James Fulcrumstein'}, {'assigned_username': 'Mary Littlelamb'}]

    #user_dict = {'James Fulcrumstein':0, 'Mary Littlelamb':0, 'Kent Breakfield':0}
    user_dict = {}
    for user in docs['all_users']:
        if user['updated_by_name'] == "":
            user_dict["unassigned"] = 0
        user_dict[user['updated_by_name']] = 0

    for doc in docs_dict['updated_docs']:
        if doc.updated_by_name in user_dict and doc.updated_by_name != "":
            user_dict[doc.updated_by_name] += 1
        if doc.updated_by_name == "":
            user_dict["unassigned"] += 1
    print(user_dict)
    #If a value is equal to 0, then we remove that key. 
    #No need to see which users don't have any currently assigned isues.
    #user_assigned_dict ={'James Fulcrumstein':3, 'Mary Littlelamb':5,}
    user_assigned_dict = {key:value for key, value in user_dict.items() if value != 0}


    #Sort the dictionary so that the the dictionary with the highest value is displayed first
    #docs['user_assigned_dict'] = [('Mary Littlelamb', 5),('James Fulcrumstein', 3)]
    docs_dict['user_assigned_dict'] = sorted(user_assigned_dict.items(), key=lambda x: x[1], reverse=True)

    docs_dict['all_docs'] =  docs_dict['updated_docs']

    return docs_dict 