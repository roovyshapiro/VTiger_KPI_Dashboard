from django.db import models
from django.utils import timezone
import VTiger_Sales_API
import json, os




class Cases(models.Model):
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
        "work_location": ""
    },
    '''
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
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.case_no}: {self.date_modified.strftime("%Y-%m-%d %H:%M:%S")}'
    '''
    @classmethod
    def user_totals(self):
        #
        Retrieves usernames from VTiger and returns a dictionary of lists
        with SUMs of all the total items in the column for today.
        Returns user_stat_dict:
        [{'Jiminy Krispers': [0, 12, 84, 12, 12, 108, 108, 24]}, {'Gargayle Hoffer': [29, 0, 37, 0, 0, 36, 36, 
        1008]}, {'Shinckley Putnick': [23, 12, 194, 0, 0, 37, 72, 2580]}, ]
        #
        credentials_file = 'credentials.json'
        credentials_path = os.path.join(os.path.abspath('.'), credentials_file)
        with open(credentials_path) as f:
            data = f.read()
        credential_dict = json.loads(data)
        vtigerapi = VTiger_Sales_API.Vtiger_api(credential_dict['username'], credential_dict['access_key'], credential_dict['host'])
        users = vtigerapi.get_users()
        
        #Determine the beginning and end of the day.
        today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = timezone.now().replace(hour=23, minute=59, second=59, microsecond=0)

        user_stat_dict = []
        for value in users.values():
            username = f"{value[0]}_{value[1]}".lower()
            #Displays the SUM of all items in the database per username
            #Only displays data for today.
            demo_scheduled_result = int(Sales_stats.objects.filter(user=f'{username}', date__gte=today_start, date__lte=today_end)[0].demo_scheduled)
            demo_given_result = int(Sales_stats.objects.filter(user=f'{username}', date__gte=today_start, date__lte=today_end)[0].demo_given)
            quote_sent_result = int(Sales_stats.objects.filter(user=f'{username}', date__gte=today_start, date__lte=today_end)[0].quote_sent)
            pilot_result = int(Sales_stats.objects.filter(user=f'{username}', date__gte=today_start, date__lte=today_end)[0].pilot)
            needs_analysis_result = int(Sales_stats.objects.filter(user=f'{username}', date__gte=today_start, date__lte=today_end)[0].needs_analysis)
            closed_won_result = int(Sales_stats.objects.filter(user=f'{username}', date__gte=today_start, date__lte=today_end)[0].closed_won)
            closed_lost_result = int(Sales_stats.objects.filter(user=f'{username}', date__gte=today_start, date__lte=today_end)[0].closed_lost)
            phone_calls_result = int(Phone_calls.objects.filter(user=f'{username}', date_created__gte=today_start, date_created__lte=today_end)[0].phone_calls)
           
            username = f"{value[0]} {value[1]}".title()
            stat_dict = {username: [demo_scheduled_result,
                                    demo_given_result,
                                    quote_sent_result,
                                    pilot_result,
                                    needs_analysis_result,
                                    closed_won_result,
                                    closed_lost_result,
                                    phone_calls_result,
                                    ]
                        }
            user_stat_dict.append(stat_dict)
        
        user_score_dict = self.calculate_scores(user_stat_dict)

        return user_stat_dict, user_score_dict
    '''
    '''
    @classmethod
    def calculate_scores(self, stat_list):
        #
        Takes the user_stat_dict from self.user_totals()
        [{'Jiminy Krispers': [0, 12, 84, 12, 12, 108, 108, 24]}, {'Gargayle Hoffer': [29, 0, 37, 0, 0, 36, 36, 
        1008]}, {'Shinckley Putnick': [23, 12, 194, 0, 0, 37, 72, 2580]}, ]

        Returns a dictionary with a total points based on values for each column:
        [{'Jiminy Krispers: 30}, {'Gargayle Hoffer': 97}, {'Shinckley Putnick': 244}, ]
        #
        user_score = []
        for stat_dict in stat_list:
            score_dict = {}
            total_score = 0
            for k, v in stat_dict.items():
                #Points for Demo Scheduled
                total_score += (5 * v[0])
                #Points for Demo Given
                total_score += (10 * v[1])
                #Points for Quote Sent
                total_score += (0 * v[2])
                #Points for Pilot
                total_score += (0 * v[3])
                #Points for Needs Analysis
                total_score += (0 * v[4])
                #Points for Closed Won
                total_score += (0 * v[5])
                #Points for Closed Lost
                total_score += (0 * v[6])
                #Points for Phone Calls
                total_score += (1 * v[7])

                score_dict[k] = total_score
            user_score.append(score_dict)

        return user_score
    '''
    '''
class Phone_calls(models.Model):
    #
    Phone calls can be retrieved as a total number for the day, as the number doesn't change.
    This is different than the opportunity sales stages as one opportunity can have multiple
    sales stages changed in a day. 
    #
    phone_calls = models.CharField(max_length=50)
    user = models.CharField(max_length=75)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user}: {self.phone_calls} - {self.date_modified.strftime("%Y-%m-%d %H:%M:%S")}'
    '''