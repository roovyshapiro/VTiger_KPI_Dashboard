# Generated by Django 3.0.7 on 2024-09-09 18:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0006_opportunities_opp_amount'),
    ]

    operations = [
        migrations.CreateModel(
            name='SMS',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sms_id', models.CharField(max_length=50)),
                ('createdtime_epoch', models.CharField(max_length=50)),
                ('createdtime', models.DateTimeField(null=True)),
                ('direction', models.CharField(max_length=15)),
                ('target_name', models.CharField(max_length=50)),
                ('target_number', models.CharField(max_length=50)),
                ('from_number', models.CharField(max_length=50)),
                ('to_number', models.CharField(max_length=50)),
                ('text', models.TextField()),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]