from django.db import models
from django.utils import timezone
import VTiger_Sales_API
import json, os


class Sales_stats(models.Model):
    '''
    All text fields:
    demo_scheduled, demo_given, quote_sent, pilot, needs_analysis, closed_won, closed_lost, phone_calls, date, user
    '''
    demo_scheduled = models.CharField(max_length=50)
    demo_given = models.CharField(max_length=50)
    quote_sent = models.CharField(max_length=50)
    pilot = models.CharField(max_length=50)
    needs_analysis = models.CharField(max_length=50)
    closed_won = models.CharField(max_length=50)
    closed_lost = models.CharField(max_length=50)
    date = models.CharField(max_length=50)
    user = models.CharField(max_length=75)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user}: {self.date_modified.strftime("%Y-%m-%d %H:%M:%S")}'

    @classmethod
    def user_totals(self):
        '''
        Retrieves usernames from VTiger and returns a dictionary of lists
        with SUMs of all the total items in the column for today.
        Returns user_stat_dict:
        [{'Jiminy Krispers': [0, 12, 84, 12, 12, 108, 108, 24]}, {'Gargayle Hoffer': [29, 0, 37, 0, 0, 36, 36, 
        1008]}, {'Shinckley Putnick': [23, 12, 194, 0, 0, 37, 72, 2580]}, ]
        '''
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

    @classmethod
    def calculate_scores(self, stat_list):
        '''
        Takes the user_stat_dict from self.user_totals()
        [{'Jiminy Krispers': [0, 12, 84, 12, 12, 108, 108, 24]}, {'Gargayle Hoffer': [29, 0, 37, 0, 0, 36, 36, 
        1008]}, {'Shinckley Putnick': [23, 12, 194, 0, 0, 37, 72, 2580]}, ]

        Returns a dictionary with a total points based on values for each column:
        [{'Jiminy Krispers: 30}, {'Gargayle Hoffer': 97}, {'Shinckley Putnick': 244}, ]
        '''
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

class Phone_calls(models.Model):
    '''
    Phone calls can be retrieved as a total number for the day, as the number doesn't change.
    This is different than the opportunity sales stages as one opportunity can have multiple
    sales stages changed in a day. 
    '''
    phone_calls = models.CharField(max_length=50)
    user = models.CharField(max_length=75)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user}: {self.phone_calls} - {self.date_modified.strftime("%Y-%m-%d %H:%M:%S")}'


class Opportunities(models.Model):
    '''
    Example Opportunity:
    {
        "adjusted_amount": "999.00000000",
        "amount": "999.00000000",
        "assigned_groupname": "",
        "assigned_user_id": "19x55",
        "assigned_username": "James Johnkberg",
        "campaignid": "",
        "cf_potentials_chancetoclose": "Medium",
        "cf_potentials_closedlostchangedat": "",
        "cf_potentials_closedwonchangedat": "",
        "cf_potentials_demogivenchangedat": "12-08-2020 03:31 PM",
        "cf_potentials_demogivendate": "",
        "cf_potentials_demonotes": "",
        "cf_potentials_demoscheduledchangedat": "12-08-2020 03:27 PM",
        "cf_potentials_discoverynotes": "Looking to buy a product!",
        "cf_potentials_distributionid": "",
        "cf_potentials_industry": "",
        "cf_potentials_leadreferencenumber": "",
        "cf_potentials_needsanalysischangedat": "12-10-2020 10:36 AM",
        "cf_potentials_nextattempt": "2020-12-09",
        "cf_potentials_pilotchangedat": "",
        "cf_potentials_qualifiedby": "",
        "cf_potentials_quotesentchangedat": "12-08-2020 04:03 PM",
        "cf_potentials_timezone": "",
        "cf_potentials_website": "",
        "closingdate": "2021-01-21",
        "contact_id": "4x929209",
        "created_user_id": "19x55",
        "createdtime": "2020-12-08 21:27:04",
        "current_stage_entry_time": "2020-12-10 16:36:34",
        "description": "Customer is looking to buy a product.",
        "email": "",
        "forecast_amount": "849.15000000",
        "forecast_category": "Pipeline",
        "id": "5x929210",
        "isclosed": "0",
        "isconvertedfromlead": "1",
        "last_contacted_on": "",
        "last_contacted_via": "",
        "leadsource": "",
        "lost_reason": "",
        "modifiedby": "19x55",
        "modifiedtime": "2020-12-10 16:36:35",
        "nextstep": "",
        "opportunity_type": "",
        "pipeline": "Standard Sales Pipeline",
        "potential_no": "POT2122",
        "potentialname": "New Amazing Opportunity!",
        "prev_sales_stage": "",
        "probability": "85.000",
        "related_to": "3x929208",
        "sales_stage": "Needs Analysis",
        "source": "CRM",
        "starred": "",
        "tags": ""
    },
    '''
    opp_id = models.CharField(max_length=50)
    contact_id = models.CharField(max_length=50)

    opp_no = models.CharField(max_length=50)
    opp_name = models.CharField(max_length=250)
    opp_stage = models.CharField(max_length=50)

    createdtime = models.DateTimeField()
    modifiedtime = models.DateTimeField()

    created_user_id = models.CharField(max_length=50)
    modifiedby = models.CharField(max_length=50)
    assigned_user_id = models.CharField(max_length=50)

    assigned_username = models.CharField(max_length=75)
    assigned_groupname = models.CharField(max_length=75)

    current_stage_entry_time = models.DateTimeField(null=True)
    demo_scheduled_changed_at = models.DateTimeField(null=True)
    demo_given_changed_at = models.DateTimeField(null=True)
    quote_sent_changed_at = models.DateTimeField(null=True)
    pilot_changed_at = models.DateTimeField(null=True)
    needs_analysis_changed_at = models.DateTimeField(null=True)
    closed_lost_changed_at = models.DateTimeField(null=True)
    closed_won_changed_at = models.DateTimeField(null=True)

    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.assigned_username} - {self.opp_name} - {self.opp_no} - {self.date_modified.strftime("%Y-%m-%d %H:%M:%S")}'

    def modifiedtime_date(self):
        return self.modifiedtime.strftime('%Y-%m-%d')
