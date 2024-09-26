"""
Django settings for sales_dashboard project.

Generated by 'django-admin startproject' using Django 3.0.2.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os, json

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# The secret key is stored in the "credentials.json" file
credentials_file = 'credentials.json'
credentials_path = os.path.join(os.path.abspath('.'), credentials_file)
with open(credentials_path) as f:
    data = f.read()
credential_dict = json.loads(data)
SECRET_KEY = credential_dict['django_secret_key']

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True 

SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False

ALLOWED_HOSTS = ['*', '192.168.1.19', 'localhost', '127.0.0.1',]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    #Django All Auth - Google Login
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',

    'cases',
    'sales',
    'home',
    'ship',
    'dev',
    'docs',
    'celery',
    'django_celery_beat',
    'rest_framework',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'VTiger_KPI_Dashboard.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'VTiger_KPI_Dashboard.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        'OPTIONS': {
            'timeout': 20,  # 20 seconds timeout
        }
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
    os.path.join(BASE_DIR, '/ship/static'),
]

#Google Authentication
AUTHENTICATION_BACKENDS = (
 'django.contrib.auth.backends.ModelBackend',
 'allauth.account.auth_backends.AuthenticationBackend',
 )
SITE_ID = 1
LOGIN_REDIRECT_URL = '/'
ACCOUNT_LOGOUT_ON_GET = True 

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        }
    }
}

# Celery application definition
CELERY_BROKER_URL = 'redis://localhost:6379'
CELERY_RESULT_BACKEND = 'redis://localhost:6379'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_SERIALIZER = 'json'
#CELERY_IMPORTS = ['comm.tasks']
CELERY_BROKER_URL = 'redis://localhost:6379'

from celery.schedules import crontab   
# https://docs.celeryproject.org/en/latest/userguide/periodic-tasks.html#crontab-schedules
# https://docs.celeryproject.org/en/latest/reference/celery.schedules.html#celery.schedules.crontab
# Each Celery task will have a Business Hours (BH) schedule, an After Hours (AH) schedule and a Weekend Hours (WKND) schedule.
# This eliminates utilizing API calls when we don't need real-time data.
# BH - Business Hours
#     13:00 - 23:59 UTC
#     8:00am - 7:59pm EST
#
# AH - After Hours
#     0:00 - 13:00 UTC
#     7:00pm EST - 8:00am EST
#
# WKND - Weekend Hours
#    0:00 - 23:00 UTC/EST Saturday & Sunday ONLY
#
# The crontab hour is inclusive.
# crontab(minute='*/11', hour='13-23') Will occur every 11 minutes between the hours of 13:00 UTC and 23:59 UTC. 
# On 12-30-2020, it will run at these times:
# 2020-12-30 13:00:00
# 2020-12-30 13:11:00
# 2020-12-30 13:22:00
# ...
# ...
# 2020-12-30 23:33:00
# 2020-12-30 23:44:00
# 2020-12-30 23:55:00
#
# crontab(minute='0', hour='0-12') Will run at the beginning of every hour between 0:00 UTC and 12:00 UTC.
# On 12-30-2020, it will run at these times:
# 2020-12-30 00:00:00
# 2020-12-30 01:00:00
# 2020-12-30 02:00:00
# ...
# ...
# 2020-12-30 10:00:00
# 2020-12-30 11:00:00
# 2020-12-30 12:00:00
#
# day_of_week
# A (list of) integers from 0-6, where Sunday = 0 and Saturday = 6, that represent the days of a week that execution should occur.
# hour = '*/' is equivalent to 
# Execute every three hours: midnight, 3am, 6am, 9am, noon, 3pm, 6pm, 9pm.
'''
CELERY_BEAT_SCHEDULE = {
    'get_cases_BH':{
        'task': 'cases.tasks.get_cases',
        'schedule': crontab(minute='0,20,40', hour='13-23', day_of_week='1,2,3,4,5'),
    },
    'get_cases_AH':{
        'task': 'cases.tasks.get_cases',
        'schedule': crontab(minute='0', hour='0,4,8,12', day_of_week='1,2,3,4,5'),
    },
    'get_cases_WKND':{
        'task': 'cases.tasks.get_cases',
        'schedule': crontab(minute='0', hour='*/4', day_of_week='0,6'),
    },
    'get_opportunities_BH': {
       'task': 'sales.tasks.get_opportunities',
       'schedule': crontab(minute='3,23,43', hour='13-23', day_of_week='1,2,3,4,5'),
    },
    'get_opportunities_AH': {
       'task': 'sales.tasks.get_opportunities',
       'schedule': crontab(minute='5', hour='0,4,8,12', day_of_week='1,2,3,4,5'),
    },
    'get_opportunities_WKND': {
       'task': 'sales.tasks.get_opportunities',
       'schedule': crontab(minute='5', hour='*/4', day_of_week='0,6'),
    },
     'get_phonecalls_BH': {
       'task': 'sales.tasks.get_phonecalls',
       'schedule': crontab(minute='7,27,47', hour='13-23', day_of_week='1,2,3,4,5'),
    },
     'get_phonecalls_AH': {
       'task': 'sales.tasks.get_phonecalls',
       'schedule': crontab(minute='10', hour='0,4,8,12', day_of_week='1,2,3,4,5'),
    },
     'get_phonecalls_WKND': {
       'task': 'sales.tasks.get_phonecalls',
       'schedule': crontab(minute='10', hour='*/4', day_of_week='0,6'),
    },
     'get_products': {
       'task': 'ship.tasks.get_products',
       'schedule': crontab(minute='39', hour='*/7', day_of_week='1,2,3,4,5'),
    },
    'get_issues': {
       'task': 'dev.tasks.get_issues',
       'schedule': crontab(minute='39', hour='*/3', day_of_week='*'),
    },
}
'''