from django.contrib import admin
from data.models import Userdata
from django.contrib.auth.admin import UserAdmin

# Register your models here.
from data.models import Question,Submission

admin.site.register(Userdata)
admin.site.register(Question)
admin.site.register(Submission)