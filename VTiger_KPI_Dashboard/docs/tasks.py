from __future__ import absolute_import, unicode_literals
from celery import Celery
from celery import shared_task
from django.utils.timezone import make_aware
 
from .models import Docs
import docs_outline_api
import json, os, datetime, requests, pytz

@shared_task
def get_docs():
    '''
    Example Recently Updated Doc:
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

    db_docs = Docs.objects.all()

    recent_docs, flock_url, docs_url = retrieve_docs()   


    for doc in recent_docs:
        #If the doc entry exists in the database, then the doc will be just saved
        #If the doc doesn't exist, then the doc will be added to the db
        #Only new doc updates will be sent to Flock

        doc_updated_at = make_aware(datetime.datetime.strptime(doc['updatedAt'], "%Y-%m-%dT%H:%M:%S.%fZ"))


        try:
            new_doc = db_docs.get(updated_at = doc_updated_at)
            new_doc.save()
            continue
        except:
            new_doc = Docs()

        try:
            new_doc.doc_id = doc['id']
        except KeyError:
            new_doc.doc_id = ""
        try:
            new_doc.parent_doc_id = doc['parentDocumentId']
        except KeyError:
            new_doc.parent_doc_id = ""
        try:
            new_doc.collection_id = doc['collectionId']
        except KeyError:
            new_doc.collection_id = ""

        try:
            new_doc.doc_url = doc['url']
        except KeyError:
            new_doc.doc_url = ""

        try:
            new_doc.doc_url_id = doc['urlId']
        except KeyError:
            new_doc.doc_url_id = ""

        try:
            new_doc.team_id = doc['teamId']
        except KeyError:
            new_doc.team_id = ""

        #"%Y-%m-%dT%H:%M:%S.%fZ"
        #"2022-03-29T14:40:49.231Z"
        try:
            new_doc.published_at = make_aware(datetime.datetime.strptime(doc['publishedAt'], "%Y-%m-%dT%H:%M:%S.%fZ"))
        except KeyError:
            new_doc.published_at = ""

        try:
            new_doc.doc_title = doc['title']
        except KeyError:
            new_doc.doc_title = ""

        try:
            new_doc.doc_text = doc['text']
        except KeyError:
            new_doc.doc_text = ""

        #"%Y-%m-%dT%H:%M:%S.%fZ"
        #"2022-03-29T14:40:49.231Z"
        try:
            new_doc.doc_last_viewed_at = make_aware(datetime.datetime.strptime(doc['lastViewedAt'], "%Y-%m-%dT%H:%M:%S.%fZ"))
        except KeyError:
            new_doc.doc_last_viewed_at = ""

        try:
            new_doc.revision = doc['revision']
        except KeyError:
            new_doc.revision = 0

        #"%Y-%m-%dT%H:%M:%S.%fZ"
        #"2022-03-29T14:40:49.231Z"
        try:
            new_doc.updated_at = make_aware(datetime.datetime.strptime(doc['updatedAt'], "%Y-%m-%dT%H:%M:%S.%fZ"))
        except KeyError:
            new_doc.updated_at = ""

        try:
            new_doc.updated_by_name = doc['updatedBy']['name']
        except KeyError:
            new_doc.updated_by_name = ""

        try:
            new_doc.updated_by_id = doc['updatedBy']['id']
        except KeyError:
            new_doc.updated_by_id = ""

        #"%Y-%m-%dT%H:%M:%S.%fZ"
        #"2022-03-29T14:40:49.231Z"
        try:
            new_doc.updated_by_last_active_at = make_aware(datetime.datetime.strptime(doc['updatedBy']['lastActiveAt'], "%Y-%m-%dT%H:%M:%S.%fZ"))
        except KeyError:
            new_doc.updated_by_last_active_at = ""

        #"%Y-%m-%dT%H:%M:%S.%fZ"
        #"2022-03-29T14:40:49.231Z"
        try:
            new_doc.created_at = make_aware(datetime.datetime.strptime(doc['createdAt'], "%Y-%m-%dT%H:%M:%S.%fZ"))
        except KeyError:
            new_doc.created_at = ""
        try:
            new_doc.created_by_name = doc['createdBy']['name']
        except KeyError:
            new_doc.created_by_name = ""
        try:
            new_doc.created_by_id = doc['createdBy']['id']
        except KeyError:
            new_doc.created_by_id = ""

        
        #"%Y-%m-%dT%H:%M:%S.%fZ"
        #"2022-03-29T14:40:49.231Z"
        try:
            new_doc.created_by_last_active_at = make_aware(datetime.datetime.strptime(doc['createdBy']['lastActiveAt'], "%Y-%m-%dT%H:%M:%S.%fZ"))
        except KeyError:
            new_doc.created_by_last_active_at = ""

        try:
            new_doc.collaborator_ids = json.dumps(doc['collaboratorIds'])
        except:
            new_doc.collaborator_ids = ""

        new_doc.save()
        post_to_flock(doc, docs_url, flock_url)



def retrieve_docs():
    '''
    Returns a list of all Outline docs in a list of dictionaries
    '''
    credentials_file = 'credentials.json'
    credentials_path = os.path.join(os.path.abspath('.'), credentials_file)
    with open(credentials_path) as f:
        data = f.read()
    credential_dict = json.loads(data)

    docs_api = docs_outline_api.Docs_outline_api(credential_dict['docs_host'], credential_dict['docs_token'], credential_dict['docs_url'], credential_dict['docs_flock_url'])

    recent_docs  = docs_api.get_recently_updated_docs()

    return recent_docs, credential_dict['docs_flock_url'], credential_dict['docs_url']


def post_to_flock(doc, docs_url, flock_url):
    headers = {
        "Content-Type": "application/json",
    }

    #Convert timestamp to datetime object &
    #Change the timezone to Central Time
    update_time = doc['updatedAt']
    update_time_dt = datetime.datetime.strptime(update_time, "%Y-%m-%dT%H:%M:%S.%fZ")
    update_time_dt = update_time_dt.replace(tzinfo=pytz.utc)
    update_time_dt_cst = update_time_dt.astimezone(pytz.timezone('US/Central'))
    update_time = datetime.datetime.strftime(update_time_dt_cst, "%-m-%-d-%Y %I:%M%p")

    json_data = {"flockml":f"<a href='{docs_url}{doc['url']}'>{doc['title']}</a> <br><strong>{doc['updatedBy']['name']}</strong><br>{update_time} CST"}
    response = requests.post(flock_url, headers=headers, json=json_data)