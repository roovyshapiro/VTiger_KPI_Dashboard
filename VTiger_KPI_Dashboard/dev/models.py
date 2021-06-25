from django.db import close_old_connections, models
from django.utils import timezone

class Redmine_issues(models.Model):
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
    assigned_to_name = models.CharField(max_length=50, null=True)
    author_name = models.CharField(max_length=50, null=True)
    
    issue_id = models.IntegerField()
    subject = models.CharField(max_length=200, null=True)
    description = models.TextField(null=True)
    status_name = models.CharField(max_length=20, null=True)
    tracker_name = models.CharField(max_length=20, null=True)
    priority_name = models.CharField(max_length=20, null=True)
    project_name = models.CharField(max_length=20, null=True)
    category_name = models.CharField(max_length=20, null=True)

    custom_field1_value = models.CharField(max_length=100, null=True)
    custom_field2_value = models.CharField(max_length=100, null=True)
    custom_field3_value= models.TextField(null=True)
    done_ratio = models.CharField(max_length=10, null=True)
    estimated_hours = models.CharField(max_length=20, null=True)

    start_date = models.DateTimeField(null=True)
    due_date = models.DateTimeField(null=True)
    created_on = models.DateTimeField(null=True)
    updated_on = models.DateTimeField(null=True)
    closed_on = models.DateTimeField(null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.issue_id} - {self.status_name} - {self.subject} - {self.updated_on.strftime("%Y-%m-%d %H:%M:%S")}'