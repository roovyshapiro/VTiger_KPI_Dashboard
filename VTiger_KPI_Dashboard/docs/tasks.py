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


##############################
################################
##################################
###################################
#
#
# Process and post a single DOC based on a webhook
#
#

@shared_task
def process_outline_update(doc):
    '''
    Incoming update via Webhook
    Data is sent to flock and saved to the DB.
    If the collection is not one of the approved public collections,
    then it is ignored and not sent to flock or saved.
    
    Revisions Example:

    {
        "id": "983e0209-534c-cc1225066",
        "actorId": "d92f38cb8c68b2",
        "webhookSubscriptionId": "3741908f1802306fa",
        "createdAt": "2023-06-26T15:38:12.609Z",
        "event": "revisions.create",
        "payload": {
                        "id": "dee58357-f0c99034129",
                        "model":{
                                    "id": "dee58357-1c9034129",
                                    "documentId": "85d778d8b1f81f",
                                    "title": "Automation",
                                    "text": "The scripts in\n\\\n",
                                    "createdAt": "2023-06-26T15:33:12.462Z",
                                    "createdBy": {
                                                    "id": "d92fdca0-7fcd38cb8c68b2",
                                                    "name": "Roovy Shapiro",
                                                    "avatarUrl": "https://outline-productio/e0130b-19a5-40af-ae8e-22998bd11f32",
                                                    "color": "#F5BE31",
                                                    "isAdmin": true,
                                                    "isSuspended": false,
                                                    "isViewer": false,
                                                    "createdAt": "2022-03-29T14:40:49.231Z",
                                                    "updatedAt": "2023-06-26T15:32:38.545Z",
                                                    "lastActiveAt": "2023-06-26T15:32:38.545Z"
                                                },
                                    "collectionId": "0bf661a211ea76f990e"
                                }
                    }
    }
    

    
    '''
    revision = False
    try:
        if doc['event'] == "revisions.create":
            revision = True
    except KeyError:
        print('keyerror1', doc)

    flock_url, docs_url, doc = retrieve_docs_webhook(revision, doc)   

    collections_file = 'public_collections.json'
    collections_path = os.path.join(os.path.abspath('.'), collections_file)
    with open(collections_path) as f:
        data = f.read()
    collections_list = json.loads(data)

    public_collect = False
    for collection in collections_list:
        try:
            if doc['payload']['model']['collectionId'] == collection['id']:
                public_collect = True
                break
        except KeyError:
            print(doc)
    try:
        if doc['payload']['model']['updatedAt'] == None:
            public_collect = False
    except KeyError:
        print('keyerror2', doc)

    if public_collect == True:
        print('publishing to flock', doc['payload']['model']['title'])
        post_to_flock(doc, docs_url, flock_url)
        process_doc_webhook(doc)
        print('saving to db', doc['payload']['model']['title'])

        
    else:
        print('this is a private update!', doc['payload']['model']['title'])


@shared_task
def process_doc_webhook(doc):
    '''
    Example Recently Updated Doc:
    {
    "id": "3f3a9e00-d0fb-4673fe236075e7",
    "actorId": "d92fdca0-7fcd1d0-b738cb8c68b2",
    "webhookSubscriptionId": "374190c6-1f49-404d-b26e-b8f1802306fa",
    "createdAt": "2023-06-07T22:06:25.899Z",
    "event": "documents.update",
    "payload": {
        "id": "d9e5b309-a12-845c-0fdec5b5eaee",
        "model": {
        "id": "d9e5b309-a12e-845c-0fdec5b5eaee",
        "url": "/doc/tech-support-AbtoVSUWZ7",
        "urlId": "AbtoVZ7",
        "title": "🛠️Tech Support",
        "text": "Support Cel l Phone Number:\n\n\n\n1\n\n\\\n",
        "tasks": {
            "completed": 0,
            "total": 0
        },
        "createdAt": "2022-04-05T17:25:21.926Z",
        "createdBy": {
            "id": "d92fdca0-7fcd-42738cb8c68b2",
            "name": "Roovy Shapiro",
            "avatarUrl": "https://outline-production-attachments.s3-accelerate.amazonaws.com/avatars/d92fdca0-7fcd-420d-c68b2/37e0130b-19a5-40af-ae8e-22998bd11f32",
            "color": "#F5BE31",
            "isAdmin": true,
            "isSuspended": false,
            "isViewer": false,
            "createdAt": "2022-03-29T14:40:49.231Z",
            "updatedAt": "2023-06-07T22:03:45.943Z",
            "lastActiveAt": "2023-06-07T22:03:45.943Z"
        },
        "updatedAt": "2023-06-07T22:06:25.873Z",
        "updatedBy": {
            "id": "d92fdca0-7fcd-420db738cb8c68b2",
            "name": "Roovy Shapiro",
            "avatarUrl": "https://outline-production-attachments.s3-accelerate.amazonaws.com/avatars/d92fdca0-7fcd-b738cb8c68b2/37e0130b-19a5-40af-ae8e-22998bd11f32",
            "color": "#F5BE31",
            "isAdmin": true,
            "isSuspended": false,
            "isViewer": false,
            "createdAt": "2022-03-29T14:40:49.231Z",
            "updatedAt": "2023-06-07T22:03:45.943Z",
            "lastActiveAt": "2023-06-07T22:03:45.943Z"
        },
        "publishedAt": "2022-04-05T17:25:29.145Z",
        "archivedAt": null,
        "deletedAt": null,
        "teamId": "c44ccee8-c6d7-41e57ca61b5a11",
        "template": false,
        "templateId": null,
        "collaboratorIds": [
            "d92fdca0-7fcdb738cb8c68b2"
        ],
        "revision": 8,
        "fullWidth": false,
        "collectionId": "0bf661a2-a9-d11ea76f990e",
        "parentDocumentId": null
        }
    }
    }
    ''' 
    db_docs = Docs.objects.all()

    #If the doc entry exists in the database, then the doc will be just saved
    #If the doc doesn't exist, then the doc will be added to the db
    #Only new doc updates will be sent to Flock

    
    doc_updated_at = make_aware(datetime.datetime.strptime(doc['payload']['model']['updatedAt'], "%Y-%m-%dT%H:%M:%S.%fZ"))


    #try:
    #    new_doc = db_docs.get(updated_at = doc_updated_at)
    #    #new_doc.save()
    #except:
    #    new_doc = Docs()
    new_doc = Docs()

    try:
        new_doc.doc_id = doc['payload']['model']['id']
    except KeyError:
        new_doc.doc_id = ""
    try:
        new_doc.parent_doc_id = doc['payload']['model']['parentDocumentId']
    except KeyError:
        new_doc.parent_doc_id = ""
    try:
        new_doc.collection_id = doc['payload']['model']['collectionId']
    except KeyError:
        new_doc.collection_id = ""

    try:
        new_doc.doc_url = doc['payload']['model']['url']
    except KeyError:
        new_doc.doc_url = ""

    try:
        new_doc.doc_url_id = doc['payload']['model']['urlId']
    except KeyError:
        new_doc.doc_url_id = ""

    try:
        new_doc.team_id = doc['payload']['model']['teamId']
    except KeyError:
        new_doc.team_id = ""

    #"%Y-%m-%dT%H:%M:%S.%fZ"
    #"2022-03-29T14:40:49.231Z"
    try:
        new_doc.published_at = make_aware(datetime.datetime.strptime(doc['payload']['model']['publishedAt'], "%Y-%m-%dT%H:%M:%S.%fZ"))
    except KeyError:
        new_doc.published_at = ""

    try:
        new_doc.doc_title = doc['payload']['model']['title']
    except KeyError:
        new_doc.doc_title = ""

    try:
        new_doc.doc_text = doc['payload']['model']['text']
    except KeyError:
        new_doc.doc_text = ""

    try:
        new_doc.revision = doc['payload']['model']['revision']
    except KeyError:
        new_doc.revision = 0

    #"%Y-%m-%dT%H:%M:%S.%fZ"
    #"2022-03-29T14:40:49.231Z"
    try:
        new_doc.updated_at = make_aware(datetime.datetime.strptime(doc['payload']['model']['updatedAt'], "%Y-%m-%dT%H:%M:%S.%fZ"))
    except KeyError:
        new_doc.updated_at = ""

    try:
        new_doc.updated_by_name = doc['payload']['model']['updatedBy']['name']
    except KeyError:
        new_doc.updated_by_name = ""

    try:
        new_doc.updated_by_id = doc['payload']['model']['updatedBy']['id']
    except KeyError:
        new_doc.updated_by_id = ""

    #"%Y-%m-%dT%H:%M:%S.%fZ"
    #"2022-03-29T14:40:49.231Z"
    try:
        new_doc.updated_by_last_active_at = make_aware(datetime.datetime.strptime(doc['payload']['model']['updatedBy']['lastActiveAt'], "%Y-%m-%dT%H:%M:%S.%fZ"))
    except KeyError:
        new_doc.updated_by_last_active_at = ""

    #"%Y-%m-%dT%H:%M:%S.%fZ"
    #"2022-03-29T14:40:49.231Z"
    try:
        new_doc.created_at = make_aware(datetime.datetime.strptime(doc['payload']['model']['createdAt'], "%Y-%m-%dT%H:%M:%S.%fZ"))
    except KeyError:
        new_doc.created_at = ""
    try:
        new_doc.created_by_name = doc['payload']['model']['createdBy']['name']
    except KeyError:
        new_doc.created_by_name = ""
    try:
        new_doc.created_by_id = doc['payload']['model']['createdBy']['id']
    except KeyError:
        new_doc.created_by_id = ""

    
    #"%Y-%m-%dT%H:%M:%S.%fZ"
    #"2022-03-29T14:40:49.231Z"
    try:
        new_doc.created_by_last_active_at = make_aware(datetime.datetime.strptime(doc['payload']['model']['createdBy']['lastActiveAt'], "%Y-%m-%dT%H:%M:%S.%fZ"))
    except KeyError:
        new_doc.created_by_last_active_at = ""

    try:
        new_doc.collaborator_ids = json.dumps(doc['payload']['model']['collaboratorIds'])
    except:
        new_doc.collaborator_ids = ""

    new_doc.save()


def retrieve_docs_webhook(revision, doc):
    '''
    Returns a list of all Outline docs in a list of dictionaries
    If a revision is sent to the webhook, we need to pull all the associated data
    as revisions contain much fewer data points.
    '''
    credentials_file = 'credentials.json'
    credentials_path = os.path.join(os.path.abspath('.'), credentials_file)
    with open(credentials_path) as f:
        data = f.read()
    credential_dict = json.loads(data)

    docs_api = docs_outline_api.Docs_outline_api(credential_dict['docs_host'], credential_dict['docs_token'], credential_dict['docs_url'], credential_dict['docs_flock_url'])
    if revision == True:
        full_doc_data = docs_api.get_doc_info(doc['payload']['model']['documentId'])
        doc['payload']['model']['updatedAt'] = full_doc_data['updatedAt']
        doc['payload']['model']['urlId'] = full_doc_data['urlId']
        doc['payload']['model']['url'] = full_doc_data['url']
        doc['payload']['model']['updatedBy'] = {}
        doc['payload']['model']['updatedBy']['name'] = full_doc_data['updatedBy']['name']
        doc['payload']['model']['publishedAt'] = full_doc_data['publishedAt']
        doc['payload']['model']['parentDocumentId'] = full_doc_data['parentDocumentId']
   
    return credential_dict['docs_flock_url'], credential_dict['docs_url'], doc


def post_to_flock(doc, docs_url, flock_url):
    '''
    Before posting to Flock,
    We need to check to see if its a private DOC or not
    '''
    headers = {
        "Content-Type": "application/json",
    }

    #Convert timestamp to datetime object &
    #Change the timezone to Central Time
    try:
        update_time = doc['payload']['model']['updatedAt']
    except KeyError:
        update_time = doc['payload']['model']['createdAt']

    update_time_dt = datetime.datetime.strptime(update_time, "%Y-%m-%dT%H:%M:%S.%fZ")
    update_time_dt = update_time_dt.replace(tzinfo=pytz.utc)
    update_time_dt_cst = update_time_dt.astimezone(pytz.timezone('US/Central'))
    update_time = datetime.datetime.strftime(update_time_dt_cst, "%-m-%-d-%Y %I:%M%p")

    json_data = {"flockml":f"<a href='{docs_url}{doc['payload']['model']['url']}'>{doc['payload']['model']['title']}</a> <br><strong>{doc['payload']['model']['updatedBy']['name']}</strong><br>{update_time} CST"}
    response = requests.post(flock_url, headers=headers, json=json_data)