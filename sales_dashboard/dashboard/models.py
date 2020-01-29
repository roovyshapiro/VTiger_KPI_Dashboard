from django.db import models

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


