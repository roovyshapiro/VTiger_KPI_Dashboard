# Generated by Django 3.0.7 on 2020-12-17 17:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cases', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='cases',
            name='case_url_id',
            field=models.CharField(default='', max_length=50),
        ),
    ]
