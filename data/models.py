from datetime import datetime, timedelta

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.db import models
import jwt
# Create your models here.
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token



class Userdata(models.Model):
    username = models.OneToOneField (User, on_delete=models.CASCADE)
    # password = models.CharField(max_length=50,default=123456)
    phone = models.CharField(max_length=10)
    college = models.CharField(blank=True, max_length=255)
    totalScore = models.IntegerField(default=0)
    junior = models.BooleanField(default=False)
    correctly_solved = models.IntegerField(default=0)
    attempted = models.IntegerField(default=0)

    USERNAME_FIELD ='username'
    REQUIRED_FIELDS = ['email',]


    def __str__(self):
        return str(self.username)

    def has_perm(self,perm,obj=None):
        return self.is_admin

    def has_module_perms(self,app_label):
        return True
#
@receiver(post_save,sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender,instance=None,created=False,**kwargs):
    if created:
        Token.objects.create(user=instance)



class Question(models.Model):
    question_title = models.CharField(max_length=255)
    correct_attempts = models.IntegerField(default=0)
    total_attempts = models.IntegerField(default=0)
    max_marks = models.FloatField(default=0)
    no_of_testcases=models.IntegerField(default=0)
    question_desc = models.TextField(default="NA")
    constraints = models.TextField(default="NA")
    explanation = models.TextField(default="NA")
    iformat = models.TextField(default="NA")
    oformat = models.TextField(default="NA")
    sampleInput = models.TextField(default="NA")
    sampleOutput = models.TextField(default="NA")


    def __str__(self):
        return ("question_" + str(self.pk) + "_" + self.question_title)


class Submission(models.Model):

    languages = [("cpp", "C++"), ("c", "C"), ("py", "Python")]

    user_id_fk = models.ForeignKey(Userdata, on_delete=models.CASCADE)
    question_id_fk = models.ForeignKey(Question, on_delete=models.CASCADE)
    score = models.FloatField(default=0)
    submission_time = models.DateTimeField(auto_now=True)
    attempt = models.IntegerField(default=0)
    status = models.CharField(default='NA', max_length=5)
    accuracy = models.FloatField(default=0)
    code = models.TextField(default="")
    language = models.CharField(max_length=6, choices=languages)

    def __str__(self):
        return("submission_" + str(self.pk) + "_" + self.user_id_fk.username + "_question_" + str(self.question_id_fk))


























#
# {"username":"anm",
# "name":"anupam",
# "password":"123456",
# "password2":"123456",
# "email":"anupampatil44@gmail.com",
# "phone":9405229861,
# "college":"PICT",
# "junior":false
# }