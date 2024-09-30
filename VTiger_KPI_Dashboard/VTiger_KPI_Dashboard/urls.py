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
from docs import views as doc_views
from rest_framework.routers import SimpleRouter
from sales.views import DealViewSet, OpenDealsViewSet, DateFilterDealViewSet

router = SimpleRouter()
router.register(r'sales', DealViewSet, basename='sales')
router.register(r'sales-open-deals', OpenDealsViewSet, basename='sales-open-deals')
router.register(r'sales-deals-date-filter', DateFilterDealViewSet, basename='sales-deals-date-filter')
router.register(r'sales-calls-date-filter', sales_views.PhoneCallDateFilterViewSet, basename='sales-calls-date-filter')
router.register(r'sales-sms-date-filter', sales_views.SMSDateFilterViewSet, basename='sales-sms-date-filter')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('api/', include(router.urls)),  # <-- Include the router URLs under the 'api/' path
    path('api-auth/', include('rest_framework.urls')),

    path('', home_views.home, name='home'),
    #path('sales/filter_data/', sales_views.filter_data, name='filter_data'),
    #path('sales/all_deals/', sales_views.all_deals, name='all_deals'),

    path('sales/', sales_views.main, name='sales_dashboard'),
    path('populatesales/', sales_views.populate_db, name='populate'),
    path('webhook/deals/', sales_views.deal_webhook, name='deals_webhook'),
    path('webhook/dialpad/', sales_views.call_webhook, name='dialpad_webhook'),
    path('webhook/dialpad/sms/', sales_views.sms_webhook, name='dialpad_sms_webhook'),


    #path('populateoppssales/', sales_views.populate_opp_month, name='populate_opps_month'),
    #path('populatecallssales/', sales_views.populate_call_month, name='populate_calls_month'),
    #path('deleteallsales/', sales_views.delete_all_items, name='delete_all'),
    #path('testsales/', sales_views.test_method, name='test'),
    #path('getusers/', sales_views.get_users, name='get_users'),

    path('cases/', case_views.main, name='case_dashboard'),
    path('populatecases/', case_views.populate_cases, name='populate_cases'),
    path('populateallcases/', case_views.populate_all_cases, name='populate_all_cases'),
    path('deletecases/', case_views.delete_all_cases, name='delete_all_cases'),
    path('testcases/', case_views.testing, name='cases_test'),
    path('webhook/cases/', case_views.case_webhook, name='case_webhook'),


    path('ship/', ship_views.main, name='ship_dashboard'),
    path('populateproducts/', ship_views.populate_products, name='populate_products'),
    path('ship/ratingapi/', ship_views.rating, name='rating'),

    path('dev/', dev_views.main, name='dev_dashboard'),
    path('devallissues/', dev_views.get_all_issues, name='dev_dashboard'),
    path('devrecentissues/', dev_views.get_recent_issues, name='dev_dashboard'),

    path('docs/', doc_views.main, name='dev_dashboard'),
    path('getdocs/', doc_views.get_recent_docs, name='get_docs'),
    path('webhook/outline/', doc_views.webhook, name='outline_webhook'),





]