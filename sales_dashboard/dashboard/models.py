from django.db import models
from django.db.models import Sum
from django.utils import timezone
import VTiger_Sales_API
import json, os


# Create your models here.
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
        
        stats = Sales_stats.objects.all()
        phone_calls = Phone_calls.objects.all()

        #Determine the beginning and end of the day.
        today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = timezone.now().replace(hour=23, minute=59, second=59, microsecond=0)

        user_stat_dict = []
        for value in users.values():
            username = f"{value[0]}_{value[1]}".lower()
            #Displays the SUM of all items in the database per username
            #Only displays data for today.
            demo_scheduled_sum = stats.filter(user=f'{username}', date__gte=today_start, date__lte=today_end).aggregate(Sum('demo_scheduled'))
            demo_given_sum = stats.filter(user=f'{username}', date__gte=today_start, date__lte=today_end).aggregate(Sum('demo_given'))
            quote_sent_sum = stats.filter(user=f'{username}', date__gte=today_start, date__lte=today_end).aggregate(Sum('quote_sent'))
            pilot_sum = stats.filter(user=f'{username}', date__gte=today_start, date__lte=today_end).aggregate(Sum('pilot'))
            needs_analysis_sum = stats.filter(user=f'{username}', date__gte=today_start, date__lte=today_end).aggregate(Sum('needs_analysis'))
            closed_won_sum = stats.filter(user=f'{username}', date__gte=today_start, date__lte=today_end).aggregate(Sum('closed_won'))
            closed_lost_sum = stats.filter(user=f'{username}', date__gte=today_start, date__lte=today_end).aggregate(Sum('closed_lost'))
            phone_calls_sum = phone_calls.filter(user=f'{username}', date_created__gte=today_start, date_created__lte=today_end).aggregate(Sum('phone_calls'))
           
            username = f"{value[0]} {value[1]}".title()
            stat_dict = {username: [demo_scheduled_sum['demo_scheduled__sum'],
                                    demo_given_sum['demo_given__sum'],
                                    quote_sent_sum['quote_sent__sum'],
                                    pilot_sum['pilot__sum'],
                                    needs_analysis_sum['needs_analysis__sum'],
                                    closed_won_sum['closed_won__sum'],
                                    closed_lost_sum['closed_lost__sum'],
                                    phone_calls_sum['phone_calls__sum'],
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

# Create your models here.
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