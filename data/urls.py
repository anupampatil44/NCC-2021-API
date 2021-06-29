from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token 
from . import views
urlpatterns=[
    path('', views.HelloView.as_view(), name='hello'),
    # path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
    path('coderun/', views.coderun.as_view(), name='coderun'),
    path('codesubmit/', views.code_submit.as_view(), name='codesubmit'),
]