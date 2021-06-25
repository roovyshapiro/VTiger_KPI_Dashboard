from __future__ import absolute_import, unicode_literals
from celery import Celery
from celery import shared_task
from django.utils.timezone import make_aware
 
from .models import Redmine_issues
import redmine_api
import json, os, datetime

@shared_task
def get_issues():
    '''
    Example Issue:
        {
        "assigned_to": {
            "id": 30,
            "name": "Jefferson Archmage"
        },
        "author": {
            "id": 33,
            "name": "Randall Spitsberg"
        },
        "category": {
            "id": 6,
            "name": "Improvement"
        },
        "closed_on": null,
        "created_on": "2021-06-07T17:22:01Z",
        "custom_fields": [
            {
                "id": 1,
                "name": "Duplicate",
                "value": "0"
            },
            {
                "id": 2,
                "name": "Already fixed",
                "value": ""
            },
            {
                "id": 3,
                "multiple": true,
                "name": "App Module",
                "value": [
                    "Main - Home Page",
                    "Main - Dashboard"
                ]
            }
        ],
        "description": "Sample of a very long description of the issue!",
        "done_ratio": 0,
        "due_date": null,
        "estimated_hours": null,
        "id": 39456,
        "is_private": false,
        "priority": {
            "id": 5,
            "name": "Immediate"
        },
        "project": {
            "id": 14,
            "name": "Main Project"
        },
        "start_date": "2021-06-07",
        "status": {
            "id": 2,
            "name": "In Progress"
        },
        "subject": "Title of the Redmine Issue",
        "tracker": {
            "id": 10,
            "name": "Improvement"
        },
        "updated_on": "2021-06-11T18:52:19Z"
    },
    '''
    db_issues = Redmine_issues.objects.all()
    all_issues = retrieve_redmine_data()

    for issue in all_issues:
        #If the issue exists in the database, then the issue will be updated
        #If the issue doesn't exist, then the issue will be added to the db
        try:
            new_issue = db_issues.get(issue_id = issue['id'])
        except:
            new_issue = Redmine_issues()
        new_issue.assigned_to_name = issue['assigned_to']['name']
        new_issue.author_name = issue['author']['name']
        
        new_issue.issue_id = issue['id']
        new_issue.subject = issue['subject']
        new_issue.description = issue['subject']
        new_issue.status_name = issue['status']['name']
        new_issue.tracker_name = issue['tracker']['name']
        new_issue.priority_name = issue['priority']['name']
        new_issue.project_name = issue['project']['name']
        new_issue.category_name = issue['category']['name']

        new_issue.custom_field1_value = issue['custom_fields'][0]['value']
        new_issue.custom_field2_value = issue['custom_fields'][0]['value']
        #Convert a long python list into a string
        new_issue.custom_field3_value= json.dumps(issue['custom_fields'][0]['value'])

        new_issue.done_ratio = issue['done_ratio']
        new_issue.estimated_hours = issue['estimated_hours']

        #2021-06-07
        new_issue.start_date = make_aware(datetime.datetime.strptime(issue['start_date'] ,'%Y-%m-%d'))
        #2020-06-26
        new_issue.due_date = make_aware(datetime.datetime.strptime(issue['due_date'] ,'%Y-%m-%d'))
        #2020-06-18T05:38:14Z
        new_issue.created_on = make_aware(datetime.datetime.strptime(issue['created_on'] ,'%Y-%m-%dT%H:%M:%SZ'))
        #2021-06-11T18:52:19Z
        new_issue.updated_on = make_aware(datetime.datetime.strptime(issue['updated_on'] ,'%Y-%m-%dT%H:%M:%SZ'))
        #2020-06-18T05:38:14Z
        new_issue.closed_on = make_aware(datetime.datetime.strptime(issue['closed_on'] ,'%Y-%m-%dT%H:%M:%SZ'))

        new_issue.save()


def retrieve_redmine_data():
    '''
    Returns a list of all Redmine Issues in a list of dictionaries
    '''
    credentials_file = 'credentials.json'
    credentials_path = os.path.join(os.path.abspath('.'), credentials_file)
    with open(credentials_path) as f:
        data = f.read()
    credential_dict = json.loads(data)
    redmine_issue_getter = redmine_api.Redmine_API(credential_dict['redmine_username'], credential_dict['redmine_access_key'], credential_dict['redmine_host'])
    all_issues = redmine_issue_getter.get_all_data()
    
    return all_issues
