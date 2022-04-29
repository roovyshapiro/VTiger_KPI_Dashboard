from django.db import close_old_connections, models
from django.utils import timezone

class Docs(models.Model):
    '''
    DOC Example
    {
        "archivedAt": null,
        "collaboratorIds": [
            "12345-1234-1234-1234-123456789",
            "12345asdf-1234-1234f-1234a-12345a",        
            ],
        "collectionId": "797asd6-4568-44560-8456-44asdfe0f",
        "createdAt": "2022-04-13T18:32:17.279Z",
        "createdBy": {
            "avatarUrl": "https://outline-production-attachments.s3-accelerate.amazonaws.com/avatars/234234-7fcd-23423-b1d0-234234/234234-3432-343-2342-234234g",
            "color": "#F5BE31",
            "createdAt": "2022-03-29T14:40:49.231Z",
            "id": "234234-7fcd-2342f-b1d0-2342342fg",
            "isAdmin": true,
            "isSuspended": false,
            "isViewer": false,
            "lastActiveAt": "2022-04-29T15:03:39.115Z",
            "name": "Roovy Shapiro",
            "updatedAt": "2022-04-29T15:03:39.115Z"
        },
        "deletedAt": null,
        "fullWidth": false,
        "id": "234234-ae0e-abcd-abc3-234234fgfg",
        "lastViewedAt": "2022-04-13T19:35:44.370Z",
        "parentDocumentId": "112456-abcd-abcd-abcd-12345678",
        "publishedAt": "2022-04-13T18:32:52.768Z",
        "revision": 3,
        "tasks": {
            "completed": 0,
            "total": 0
        },
        "teamId": "c12345-1234-1234-5432-abcdef1234",
        "template": false,
        "templateId": null,
        "text": "https://github.com/roovyshapiro/VTiger_KPI_Dashboard",
        "title": "Title",
        "updatedAt": "2022-04-13T18:33:00.885Z",
        "updatedBy": {
            "avatarUrl": "https://outline-production-attachments.s3-accelerate.amazonaws.com/avatars/123123-1234-1234-1234-123123123/123456-1234-1234-1234-abcdef1234",
            "color": "#F5BE31",
            "createdAt": "2022-03-29T14:40:49.231Z",
            "id": "12345asdf-1234-1234f-1234a-12345a",
            "isAdmin": true,
            "isSuspended": false,
            "isViewer": false,
            "lastActiveAt": "2022-04-29T15:03:39.115Z",
            "name": "Roovy Shapiro",
            "updatedAt": "2022-04-29T15:03:39.115Z"
        },
        "url": "/doc/Title-1234567abcedf",
        "urlId": "1234567abcedf"
    },
    '''
    doc_id = models.CharField(max_length=50, null=True,blank=True)
    parent_doc_id = models.CharField(max_length=50, null=True,blank=True)

    collection_id = models.CharField(max_length=50, null=True,blank=True)
    doc_url = models.CharField(max_length=50, null=True,blank=True)
    doc_url_id = models.CharField(max_length=50, null=True,blank=True)
    team_id = models.CharField(max_length=50, null=True,blank=True)
    published_at = models.DateTimeField(null=True,blank=True)

    doc_title = models.CharField(max_length=75, null=True,blank=True)
    doc_text = models.TextField(null=True,blank=True)
    doc_last_viewed_at = models.DateTimeField(null=True,blank=True)
    revision = models.IntegerField(null=True,blank=True)

    updated_at = models.DateTimeField(null=True,blank=True)
    updated_by_name = models.CharField(max_length=50, null=True,blank=True)
    updated_by_id = models.CharField(max_length=50, null=True,blank=True)
    updated_by_last_active_at = models.DateTimeField(null=True,blank=True)

    created_at = models.DateTimeField(null=True,blank=True)
    created_by_name = models.CharField(max_length=50, null=True,blank=True)
    created_by_id = models.CharField(max_length=50, null=True,blank=True)
    created_by_last_active_at = models.DateTimeField(null=True,blank=True)

    collaborator_ids = models.TextField(null=True,blank=True)

    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.doc_title} - {self.doc_url} - {self.updated_by_name} - {self.updated_at.strftime("%Y-%m-%d %H:%M:%S")}'