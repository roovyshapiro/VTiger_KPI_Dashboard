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
            my_sum = stats.filter(user=f'{username}').aggregate(Sum('phone_calls'))
            stat_dict = {username: my_sum['phone_calls__sum']}
            user_stat_dict.append(stat_dict)
        
        return user_stat_dict



