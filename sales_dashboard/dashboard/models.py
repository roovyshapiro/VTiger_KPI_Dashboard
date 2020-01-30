from django.db import models
from django.db.models import Sum
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
    phone_calls = models.CharField(max_length=50)
    date = models.CharField(max_length=50)
    user = models.CharField(max_length=75)

    def __str__(self):
        return f'{self.user} - {self.date}'

    @classmethod
    def user_totals(self):
        '''
        Retrieves usernames from VTiger and returns a dictionary of lists
        with SUMs of all the total items in the column.
        No time frame is specified yet.
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

        user_stat_dict = []
        for value in users.values():
            username = f"{value[0]}_{value[1]}".lower()
            demo_scheduled_sum = stats.filter(user=f'{username}').aggregate(Sum('demo_scheduled'))
            demo_given_sum = stats.filter(user=f'{username}').aggregate(Sum('demo_given'))
            quote_sent_sum = stats.filter(user=f'{username}').aggregate(Sum('quote_sent'))
            pilot_sum = stats.filter(user=f'{username}').aggregate(Sum('pilot'))
            needs_analysis_sum = stats.filter(user=f'{username}').aggregate(Sum('needs_analysis'))
            closed_won_sum = stats.filter(user=f'{username}').aggregate(Sum('closed_won'))
            closed_lost_sum = stats.filter(user=f'{username}').aggregate(Sum('closed_lost'))
            phone_calls_sum = stats.filter(user=f'{username}').aggregate(Sum('phone_calls'))
           
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

        return user_stat_dict




