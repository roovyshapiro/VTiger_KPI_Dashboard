from django.db import models

# Create your models here.
        #demo_scheduled TEXT,demo_given TEXT,quote_sent TEXT,pilot TEXT,needs_analysis TEXT,closed_won TEXT,closed_lost TEXT,phone_calls TEXT,date TEXT
class sales_stats(models.Model):
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


