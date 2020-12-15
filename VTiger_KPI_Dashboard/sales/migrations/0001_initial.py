# Generated by Django 3.0.3 on 2020-12-14 20:35

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Opportunities',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('opp_id', models.CharField(max_length=50)),
                ('contact_id', models.CharField(max_length=50)),
                ('opp_no', models.CharField(max_length=50)),
                ('opp_name', models.CharField(max_length=250)),
                ('opp_stage', models.CharField(max_length=50)),
                ('createdtime', models.DateTimeField()),
                ('modifiedtime', models.DateTimeField()),
                ('created_user_id', models.CharField(max_length=50)),
                ('modifiedby', models.CharField(max_length=50)),
                ('assigned_user_id', models.CharField(max_length=50)),
                ('assigned_username', models.CharField(max_length=75)),
                ('assigned_groupname', models.CharField(max_length=75)),
                ('current_stage_entry_time', models.DateTimeField(null=True)),
                ('demo_scheduled_changed_at', models.DateTimeField(null=True)),
                ('demo_given_changed_at', models.DateTimeField(null=True)),
                ('quote_sent_changed_at', models.DateTimeField(null=True)),
                ('pilot_changed_at', models.DateTimeField(null=True)),
                ('needs_analysis_changed_at', models.DateTimeField(null=True)),
                ('closed_lost_changed_at', models.DateTimeField(null=True)),
                ('closed_won_changed_at', models.DateTimeField(null=True)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Phone_call',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('createdtime', models.DateTimeField(null=True)),
                ('modifiedtime', models.DateTimeField(null=True)),
                ('endtime', models.DateTimeField(null=True)),
                ('assigned_user_id', models.CharField(max_length=50)),
                ('created_user_id', models.CharField(max_length=50)),
                ('modified_by', models.CharField(max_length=50)),
                ('assigned_username', models.CharField(max_length=50)),
                ('assigned_groupname', models.CharField(max_length=50)),
                ('phonecall_id', models.CharField(max_length=50)),
                ('call_status', models.CharField(max_length=50)),
                ('direction', models.CharField(max_length=50)),
                ('total_duration', models.CharField(max_length=50)),
                ('customer', models.CharField(max_length=50)),
                ('customer_number', models.CharField(max_length=50)),
                ('recording_url', models.CharField(max_length=250)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]