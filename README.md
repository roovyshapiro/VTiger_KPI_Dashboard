# VTiger + Redmine KPI Dashboard

[![](https://i.imgur.com/yd7lz0b.png)](https://i.imgur.com/yd7lz0b.png)
[![](https://i.imgur.com/LaQLTgK.png)](https://i.imgur.com/LaQLTgK.png)
[![](https://i.imgur.com/kSeFFDf.png)](https://i.imgur.com/kSeFFDf.png)
[![](https://i.imgur.com/g1HgnHp.png)](https://i.imgur.com/g1HgnHp.png)

### Overview
VTiger KPI Dashboard is a Django web application which shows live data from your VTiger Cloud CRM and Redmine instances so you can track your teams activity and productivity. The intention is to have this application displayed on a large monitor next to your team members so it is easy to see at a glance how your team is operating and who are the best performers. This application is mobile-friendly as well so managers can monitor workers easily from wherever they are. Celery is used to retrieve data from VTiger and Redmine via API every ten minutes or so. Currently, we are storing all Cases, Deals, Phone Calls and Redmine issues in the Django DB. Django-AllAuth is used so that the application can only be accessed with Google logins. As this is an "internal" application, access is restricted to only the team members in your organization. Here's a simple article from Zoe Chew explaining the Google authentication process in further detail: https://whizzoe.medium.com/in-5-mins-set-up-google-login-to-sign-up-users-on-django-e71d5c38f5d5 
Here's a link to Django-AllAuth's official documentation: https://django-allauth.readthedocs.io/en/latest/

### Cases
We show all the cases that have been worked on, created and resolved in a given time frame. We also show how many cases each user has resolved. Data is shown for the current selected day, the day's week and the day's month. As an option, a table can be displayed showing all the cases for a given time frame. This data is segragated by group.

### Sales
The sales dashboard operates on a point system where each phone call is one point and each deal stage is assigned a different point value. The goal is for the salesperson to reach 100 points in a day by whatever means necessary. They can reach their goal by making 100 phone calls, or by making 50 phone calls and conducting 5 demos, etc. The various sales stages will change depending on the way you've configured your Opportunities, stages and sales pipelines within VTiger.

### Redmine Issues
We show data in a similar format to VTiger cases although in this case, the issues are not segragated by group.

### Connecting to VTiger
The file VTiger_KPI_Dashboard/VTiger_API.py uses VTiger's API to gather the data we need and pass it into the Django database. Ultimately, the primary purpose is to simply retrieve the cases, opportunities and phone calls that were made today and save them into Django's DB. All the calculations are performed afterwards by Django's views.

See here for VTiger's API documentation: https://www.vtiger.com/docs/rest-api-for-vtiger

### Connecting to Redmine
The file VTiger_KPI_Dashboard/redmine_api.py is used to gather data about the issues and pass it into the Django DB.
We only retrieve issuse that were updated in the past month on the regular interval. This can be easily changed
depending on the scale of issue changes.

See here for Redmine's API documentation: https://www.redmine.org/projects/redmine/wiki/Rest_Issues

### Credentials
Make sure to have a file named 'credentials.json' within the main 'VTiger_KPI_Dashboard' directory. This file is not a part of the public repository and contains
all the necessary credentials for connecting to VTiger, linking items to VTiger and the django SECRET_KEY.
It should be structured like this:
```python
{"username": "<vtiger_username>", "access_key": "<access_key>", "host": "https://<custom_hostname>vtiger.com/restapi/v1/vtiger/default", "host_url_cases": "https://<<custom_hostname>>.vtiger.com/index.php?module=Cases&view=Detail&record=", "host_url_calls": "https://<<custom_hostname>>.vtiger.com/index.php?module=PhoneCalls&view=Detail&record=", "host_url_opps": "https://<<custom_hostname>>.vtiger.com/index.php?module=Potentials&view=Detail&record=","django_secret_key":"<Enter Your Django Secret Key HERE>","redmine_username":"<<username>>","redmine_access_key":"<<password>>!","redmine_host":"<<https://redmine.yourcompanyurl.com>>"}
```
To generate a secret Key, you can use the following command:
```
python3 manage.py shell -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Changing Deal Stages Multiple Times per Day
Its possible to change an deal stage multiple times in the same day. 
However, the "stage last changed at" field only tells you which stage its currently at. 
Therefore, we need to create a way to capture when each of the stages have been changed throughout the day.
There are some custom VTiger configuration changes necessary to make within VTiger.
- 1. Create read-only text fields within the deal to capture the 'Modified Time' times when the sales stage was changed.
[![](https://i.imgur.com/nolUje5.png)](https://i.imgur.com/nolUje5.png)
- 2. Create a multi-path workflow to update these fields with the time from modified time.
[![](https://i.imgur.com/nTO3BsQ.png)](https://i.imgur.com/nTO3BsQ.png)
- 3. Create a multi-path workflow to update the fields upon deal creation. In this example, I've only set it for Demo Scheduled, but depending on your situation, you'll need to do this for each stage.
[![](https://i.imgur.com/uuTfdF1.png)](https://i.imgur.com/uuTfdF1.png)


### Celery Beat / Gathering VTiger Data on a Schedule
Celery Beat is used to gather the data from VTiger every ten minutes and save it to the database. It also runs this in the background so it doesn't freeze the webpage and affect the user's experience. 
Here's a great article explaining the basics if you're unfamiliar with celery/celery beat:
https://www.merixstudio.com/blog/django-celery-beat/

Javascript is then used to refresh the page every few minutes if the 'Auto Refresh' button is checked. There is a countdown timer until the page refreshes.


### Killing Orphaned Celery Processes
[![](https://i.imgur.com/K7dKal0.png)](https://i.imgur.com/K7dKal0.png)
It's a good idea to manually kill celery processes when significant changes have been made or if they're no longer needed.
Use this command to show a snapshot of all current running processes:

`ps -aux
`

Show processes with 'worker' in the name:

`ps -aux | grep 'worker'
`

Kill processes with 'worker' in the name:

`pkill -f 'worker'
`

Read more information about this here:
https://docs.celeryproject.org/en/stable/userguide/workers.html#stopping-the-worker


### Flower - Real-Time Celery Monitor
[![](https://i.imgur.com/XKb5FJw.png)](https://i.imgur.com/XKb5FJw.png)
"Flower is a web based tool for monitoring and administrating Celery clusters."
Read more about it here: https://flower.readthedocs.io/en/latest/features.html
It's very helpful for troublehsooting and showing how many times the periodic celery tasks have run.
The server is started by running the .startapps.sh file and can be accessed at http://localhost:5555


### Starting the Application
It's a good idea to use a virtual environment with Python applications especially with Django. Here's a great article explaining the process:
https://realpython.com/python-virtual-environments-a-primer/

The basic process is:
```python
#Install Virtualenv
$ pip install virtualenv
#Create a virtual environment directory named 'env'
$ python3 -m venv env
#Activate the 'env' environment
$ source /env/bin/activate
#Your shell should look like this:
(env)$
```

Make sure to install the dependencies in requirements.txt using,
`pip3 install -r requirements.txt
`

Run the django migrations to ensure your database is setup properly.
`python3 manage.py migrate
`

Finally, start the server. You can use the 'startapps.sh' file which will 
- run the redis-server (broker for celery)
- run the celery worker
- run the celery beat scheduler
- run the flower server (celery monitor)
- run the built-in django web server.

```bash
#!/bin/bash

redis-server &
celery -A VTiger_KPI_Dashboard worker &
celery -A VTiger_KPI_Dashboard beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler &
celery -A VTiger_KPI_Dashboard flower &
python3 manage.py runserver 0.0.0.0:8000
```
Afterwards, you should be able to access the dashboard locally at http://127.0.0.1:8000
Flower can be accessed locally at http://127.0.0.1:5555

### Changing Deal Sales Stages
Unfortunately, there are many places where the sales stages are hard coded in. If your sales stages are different, you'll need to edit them in the sales deal model, 
In the task where the opportunities are saved to the django DB, in the sales view and in the sales html where they are displayed.
- VTiger_KPI_Dashboard/sales/models.py
- VTiger_KPI_Dashboard/sales/tasks.py
- VTiger_KPI_Dashboard/sales/views.py
- VTiger_KPI_Dashboard/sales/templates/sales/sales.html


### Changing the Points Calculation
Currently, each phone call is worth 1 point, each Demo Scheduled is worth 5 points and each Demo Given is worth 10 points. 
To edit the score calculation, edit the values in  VTiger_KPI_Dashboard/sales/views.py
The values shown in the score_key in the HTML are static and have no bearing on the calculation.

### Javascript Libraries
DataTables.Net is used to display the tables in a user-friendly way and comes with built in functionality such as
sorting, filtering and pagination.
https://datatables.net/

Chart.JS is used to display the data retrieved from the Django DB into user-friendly charts and graphs.
https://www.chartjs.org/