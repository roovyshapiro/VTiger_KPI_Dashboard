"""sales_dashboard URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from sales import views as sales_views
from cases import views as case_views
from home import views as home_views
from ship import views as ship_views
from dev import views as dev_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),

    path('', home_views.home, name='home'),

    path('sales/', sales_views.main, name='sales_dashboard'),
    path('populatesales/', sales_views.populate_db, name='populate'),
    path('populateoppssales/', sales_views.populate_opp_month, name='populate_opps_month'),
    path('populatecallssales/', sales_views.populate_call_month, name='populate_calls_month'),
    path('deleteallsales/', sales_views.delete_all_items, name='delete_all'),
    path('testsales/', sales_views.test_method, name='test'),

    path('cases/', case_views.main, name='case_dashboard'),
    path('populatecases/', case_views.populate_cases, name='populate_cases'),
    path('populateallcases/', case_views.populate_all_cases, name='populate_all_cases'),
    path('deletecases/', case_views.delete_all_cases, name='delete_all_cases'),
    path('testcases/', case_views.testing, name='cases_test'),

    path('ship/', ship_views.main, name='ship_dashboard'),
    path('populateproducts/', ship_views.populate_products, name='populate_products'),

    path('dev/', dev_views.main, name='dev_dashboard'),
    path('devallissues/', dev_views.get_all_issues, name='dev_dashboard'),
    path('devrecentissues/', dev_views.get_recent_issues, name='dev_dashboard'),

]