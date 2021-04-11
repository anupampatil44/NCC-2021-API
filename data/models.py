from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.db import models

# Create your models here.
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token




class UserManager(BaseUserManager):
    def create_user(self,email,username,password=None):
        if not email:
            raise ValueError("Email required for user.")
        if not username:
            raise ValueError("username required")

        usern =self.model(email=self.normalize_email(email),username=username,)

        usern.set_password(password)
        usern.save(using=self._db)
        return usern


    def create_superuser(self,email,username,password):
        if password is None:
            raise TypeError("password cannot be none")

        usern = self.create_user(email=self.normalize_email(email), username=username,password=password )

        usern.is_admin=True
        usern.is_staff=True
        usern.is_superuser=True
        usern.save(using=self._db)

        return usern



class Userdata(AbstractBaseUser):
    username = models.CharField (max_length=100,unique=True)
    name = models.CharField(max_length=100)
    # password = models.CharField(max_length=50,default=123456)
    phone = models.CharField(max_length=10)
    email = models.EmailField(default='example@gmail.com',verbose_name="email")
    college = models.CharField(blank=True, max_length=255)
    totalScore = models.IntegerField(default=0)
    junior = models.BooleanField(default=True)
    is_admin=models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser= models.BooleanField(default=False)
    correctly_solved = models.IntegerField(default=0)
    attempted = models.IntegerField(default=0)

    USERNAME_FIELD ='username'
    REQUIRED_FIELDS = ['email',]

    objects=UserManager()

    def __str__(self):
        return self.username

    def has_perm(self,perm,obj=None):
        return self.is_admin

    def has_module_perms(self,app_label):
        return True

@receiver(post_save,sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender,instance=None,created=False,**kwargs):
    if created:
        Token.objects.create(user=instance)


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