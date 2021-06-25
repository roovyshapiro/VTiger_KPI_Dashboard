# Generated by Django 3.0.7 on 2021-06-25 17:45

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Redmine_issues',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('assigned_to_name', models.CharField(max_length=50, null=True)),
                ('author_name', models.CharField(max_length=50, null=True)),
                ('issue_id', models.IntegerField()),
                ('subject', models.CharField(max_length=200, null=True)),
                ('description', models.TextField(null=True)),
                ('status_name', models.CharField(max_length=20, null=True)),
                ('tracker_name', models.CharField(max_length=20, null=True)),
                ('priority_name', models.CharField(max_length=20, null=True)),
                ('project_name', models.CharField(max_length=20, null=True)),
                ('category_name', models.CharField(max_length=20, null=True)),
                ('custom_field1_value', models.CharField(max_length=100, null=True)),
                ('custom_field2_value', models.CharField(max_length=100, null=True)),
                ('custom_field3_value', models.TextField(null=True)),
                ('done_ratio', models.IntegerField(null=True)),
                ('estimated_hours', models.DecimalField(decimal_places=2, max_digits=10, null=True)),
                ('start_date', models.DateTimeField(null=True)),
                ('due_date', models.DateTimeField(null=True)),
                ('created_on', models.DateTimeField(null=True)),
                ('updated_on', models.DateTimeField(null=True)),
                ('closed_on', models.DateTimeField(null=True)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
