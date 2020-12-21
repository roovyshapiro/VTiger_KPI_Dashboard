#Changes the way the list of Users is displayed in /admin/auth/user
from django.contrib import admin
from django.contrib.auth.models import User

class MyUserAdmin(admin.ModelAdmin):
    list_display = ['email', 'first_name', 'last_name', 'is_active', 'last_login', 'date_joined']

admin.site.unregister(User)
admin.site.register(User, MyUserAdmin)