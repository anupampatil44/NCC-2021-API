from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from knox import views as knox_views
from .views import (
    RegisterAPI,
    LoginAPI,
)


app_name='account'
urlpatterns=[
    path('register/',RegisterAPI.as_view(),name='register'),
    path('login/',LoginAPI.as_view(),name='login'),
    path('logout/', knox_views.LogoutView.as_view(), name='logout'),
    path('logoutall/', knox_views.LogoutAllView.as_view(), name='logoutall'),

]