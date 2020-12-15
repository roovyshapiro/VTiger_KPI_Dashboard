from __future__ import absolute_import, unicode_literals
from celery import Celery
from celery import shared_task
from django.utils import timezone
from django.utils.timezone import make_aware
from django.db.models import Q
 
from .models import Cases
import VTiger_API
import json, os, datetime

@shared_task
def get_cases(get_all_cases=False):
    '''
    Example Case:

    {
        "age": "",
        "asset_id": "",
        "assigned_user_id": "19x91",
        "billable_time": "",
        "billing_service": "",
        "case_no": "CC21063",
        "casechannel": "",
        "casepriority": "Medium",
        "casestatus": "Open",
        "cf_1152": "",
        "cf_cases_autocommunicate": "1",
        "cf_cases_awaitingfeedback": "0",
        "contact_id": "4x316167",
        "created_user_id": "19x93",
        "createdtime": "2020-11-25 18:26:04",
        "current_state_entry_time": "2020-11-25 18:59:55",
        "customer_reply": "0",
        "deferred_date": "",
        "description": "Video needed in FMS for Truck 20",
        "email": "",
        "first_response_actualon": "",
        "first_response_expectedon": "2020-11-30 16:26:00",
        "first_response_status": "Time Left",
        "from_portal": "0",
        "group_id": "20x5",
        "id": "39x916810",
        "impact_area": "",
        "impact_type": "",
        "is_billable": "0",
        "is_billed": "0",
        "isclosed": "0",
        "last_responded_on": "",
        "modifiedby": "19x6",
        "modifiedtime": "2020-11-25 19:03:26",
        "parent_id": "3x220302",
        "product_id": "",
        "rate": "",
        "reassign_count": "0",
        "reopen_count": "0",
        "resolution": "",
        "resolution_time": "0.000",
        "resolution_type": "",
        "satisfaction_feedback": "",
        "satisfaction_index": "",
        "servicecontract_id": "",
        "servicelocation": "",
        "servicetype": "",
        "sla_actual_closureon": "",
        "sla_closureon": "2020-12-10 17:26:00",
        "slaid": "38x9",
        "slastatus": "Running",
        "source": "CRM",
        "starred": "",
        "tags": "",
        "time_spent": "0.594",
        "title": "Video needed in FMS for Truck 20",
        "total_time": "0",
        "wait_count": "",
        "work_location": "",
        "assigned_username" = "Bradley Spenkins",
        "assigned_groupname" = "Tech Support",
    },
    assigned_user_id = models.CharField(max_length=50)
    case_no = models.CharField(max_length=50)
    casestatus = models.CharField(max_length=50)
    contact_id = models.CharField(max_length=50)
    created_user_id = models.CharField(max_length=50)
    createdtime = models.CharField(max_length=50)
    group_id = models.CharField(max_length=50)
    case_id = models.CharField(max_length=50)
    modifiedby = models.CharField(max_length=50)
    modifiedtime = models.CharField(max_length=50)
    title = models.CharField(max_length=250)
    time_spent = models.CharField(max_length=50)
    assigned_username = models.CharField(max_length=75)
    assigned_groupname = models.CharField(max_length=75)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.case_no}: {self.date_modified.strftime("%Y-%m-%d %H:%M:%S")}'

        datetime.datetime.strptime('%Y-%m-%d %H:%M:%S', '2020-11-25 19:03:26')
    '''  
    if get_all_cases == True:
        today_case_list = retrieve_case_data(get_all_cases = True)
        Cases.objects.all().delete()
    else:
        today_case_list = retrieve_case_data(get_all_cases = False)
    db_cases = Cases.objects.all()

    for case in today_case_list:
        #If the case_id exists in the database, then the case will be updated
        #If the case_id doesn't exist, then the case will be added to the db
        try:
            new_case = db_cases.get(case_id = case['id'])
        except:
            new_case = Cases()

        new_case.assigned_user_id = case['assigned_user_id']
        new_case.case_no = case['case_no']
        new_case.casestatus = case['casestatus']
        new_case.contact_id = case['contact_id']
        new_case.created_user_id = case['created_user_id']
        new_case.createdtime = make_aware(datetime.datetime.strptime(case['createdtime'],'%Y-%m-%d %H:%M:%S'))
        new_case.group_id = case['group_id']
        new_case.case_id = case['id']
        new_case.modifiedby = case['modifiedby']
        new_case.modifiedtime = make_aware(datetime.datetime.strptime(case['modifiedtime'] ,'%Y-%m-%d %H:%M:%S'))
        new_case.title = case['title']
        new_case.time_spent = case['time_spent']
        #Converts the time spent from a number of hours into something more human-readable
        #838.928 -> 34 Days, 22 Hours, 55 Minutes
        try:
            time_spent = float(case['time_spent'])
            new_case.time_spent_hr = f"{int(time_spent / 24)} Days, {int(time_spent % 24)} Hours, {int(((time_spent % 24) - int(time_spent % 24)) * 60)} Minutes"
        except ValueError:
            new_case.time_spent_hr = case['time_spent']
        new_case.assigned_username = case['assigned_username']
        new_case.assigned_groupname = case['assigned_groupname']
        if case['sla_actual_closureon'] == '':
            new_case.case_resolved = None
        else:
            new_case.case_resolved = make_aware(datetime.datetime.strptime(case['sla_actual_closureon'] ,'%Y-%m-%d %H:%M:%S'))

        new_case.save()
    #After we update the cases from today, we see if any outdated cases from today can be deleted from the db
    delete_old_cases()

    #This is used to check if the amount of open cases in the db doesn't match the number of open cases in VTiger.
    #If it doesn't match, we'll need to repopulate the entire db. 
    #This can happen if a user deletes a case from VTiger who's modified time was more than a day ago.
    #If a user deletes a case from today, we'll catch it in "delete_old_cases()"
    num_all_open_cases_db = len(Cases.objects.all().filter(~Q(casestatus="Resolved") & ~Q(casestatus="Closed")))
    num_all_open_cases = retrieve_case_data(get_all_count = True)
    if num_all_open_cases != num_all_open_cases_db:
        print("Open Cases don't match!")
        get_cases(get_all_cases=True)

def delete_old_cases():
    '''
    Deletes the cases from today which have an outdated date_modified field.
    '''
    #Get a list of all the date_modified days that we have data for in the DB, each day should appear in the list only one time.
    all_cases = Cases.objects.all().order_by('date_modified')
    all_dates = []
    for case in all_cases:
        case_date = case.date_modified.replace(hour=0,minute=0,second=0,microsecond=0)
        all_dates.append(case_date)
    days_only = set(all_dates)


    for day in days_only:
        end_of_day = day.replace(hour=23, minute = 59, second=59)
        #Get all cases from the day.
        days_cases = all_cases.filter(date_modified__gte=day, date_modified__lte=end_of_day)
        #If '/populateallcases' was run, there could be 1000s of cases modified within the day. 
        #However, only the cases from today are updated on a continuous basis.
        #Therefore, all the cases that were retrieved from at least yesterday via '/populateallcases'
        #will have their date_modified fields be out of date and we don't want to delete any of them.
        #Therefore, we'll only look at the cases which were modified today in vtiger AND saved today in the DB
        days_cases_only = days_cases.filter(modifiedtime__gte=day)
        #Calculate the time difference between the first and last case in this set.
        mytimedelta = days_cases_only.last().date_modified - days_cases_only.first().date_modified
        #If no cases were deleted, and all cases from today are being updated, then the time different should be
        #close to 0. If everything is running smooth, the time will be somewhere in the microseconds.
        #However if we have a day where there is at least a 30 minute time difference in the "date_modified" field
        #between the first and last case, we'll have to go through them and delete all the 30+ minute old cases.
        #Since every case we get from VTiger is "save()'ed" to the db, the date_modified should update. If the
        #time isn't updating, we're no longer receiving it from VTiger and the only reason for that is because its
        #been deleted. Therefore, we'll delete it from our DB.
        #If someone deletes a case from more than one day ago, we wont' be able to detect it using this method.
        #The only solution I can think of at the moment is to get more than one days worth of cases from VTiger
        #every 10 minutes. But this will result in a larger amount of API calls. If its becoming an issue, that will
        #be the next step.
        if int(mytimedelta.total_seconds()) // 60 > 30:
            for case in days_cases_only:
                case_time_delta = days_cases_only.last().date_modified - case.date_modified
                if int(case_time_delta.total_seconds()) // 60 > 30:
                    case.delete()

def retrieve_case_data(get_all_cases=False, get_all_count=False):
    '''
    Prior to running this function,
    Create a file named 'credentials.json' with VTiger credentials
    and put it in the main sales_dashboard directory.
    It should have the following format:
    {"username": "(user)", "access_key": "(access_key)", "host": "(host)"}
    '''
    credentials_file = 'credentials.json'
    credentials_path = os.path.join(os.path.abspath('.'), credentials_file)
    with open(credentials_path) as f:
        data = f.read()
    credential_dict = json.loads(data)
    vtigerapi = VTiger_API.Vtiger_api(credential_dict['username'], credential_dict['access_key'], credential_dict['host'])
    if get_all_cases == True and get_all_count == False:
        today_case_list = vtigerapi.retrieve_all_cases()
    if get_all_cases == False and get_all_count == False:
        today_case_list = vtigerapi.retrieve_todays_cases()
    if get_all_cases == False and get_all_count == True:
        today_case_list = vtigerapi.retrieve_all_open_cases_count()    

    return today_case_list

