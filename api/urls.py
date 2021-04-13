from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from knox import views as knox_views
from .views import (
    RegisterAPI,
    LoginAPI,
questionhub,
codingpage,
current_user,
)


app_name='account'
urlpatterns=[
    path('register/',RegisterAPI.as_view(),name='register'),
    path('login/',LoginAPI.as_view(),name='login'),
    path('logout/', knox_views.LogoutView.as_view(), name='logout'),
    path('logoutall/', knox_views.LogoutAllView.as_view(), name='logoutall'),
    path('questionhub/',questionhub.as_view(),name='questionhub'),
    path('codingpage/',codingpage.as_view(),name='codingpage'),
    path('currentuser/',current_user,name="current_user"),
]