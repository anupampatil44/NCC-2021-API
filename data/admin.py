from django.contrib import admin
from data.models import Userdata
from django.contrib.auth.admin import UserAdmin

# Register your models here.

admin.site.register(Userdata)