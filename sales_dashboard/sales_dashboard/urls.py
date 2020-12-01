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
from django.urls import path
from dashboard import views
from case_dashboard import case_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home_view, name='home'),
    path('populate/', views.populate_db, name='populate'),
    path('deleteall/', views.delete_all_items, name='delete_all'),
    path('test/', views.test_method, name='test'),
    path('cases/', case_views.main_dashboard, name='cases'),
    path('populatecases/', case_views.populate_cases, name='populate_cases'),
    path('deletecases/', case_views.delete_all_cases, name='delete_all_cases'),
]