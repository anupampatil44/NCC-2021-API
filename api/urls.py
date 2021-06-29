from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from knox import views as knox_views
from .views import (
    RegisterAPI,
    LoginAPI,
questionhub,
codingpage,
current_user,
LeaderboardPage,
SubmissionsPage,
Userstats,
loadbuffer,
Timer
)


urlpatterns=[
    path('register/',RegisterAPI.as_view(),name='register'),
    path('login/',LoginAPI.as_view(),name='login'),
    path('logout/', knox_views.LogoutView.as_view(), name='logout'),
    path('questionhub/',questionhub.as_view(),name='questionhub'),
    path('codingpage/',codingpage.as_view(),name='codingpage'),
    path('currentuser/',current_user,name="current_user"),
    path('leaderboard/',LeaderboardPage.as_view(),name='leaderboard'),
    path('submissions/',SubmissionsPage.as_view(),name='submissions'),
    path('userstats/',Userstats.as_view(),name='userstats'),
    path('loadbuffer/',loadbuffer.as_view(),name='loadbuffer'),
    path('timer/', Timer.as_view(),name='loadbuffer'),
]