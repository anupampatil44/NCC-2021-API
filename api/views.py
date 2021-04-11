from tokenize import Token

from django.shortcuts import render
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authtoken.models import Token

from .serializers import UserSerializer


@api_view(['POST',])
def registration_view(request):
    if request.method=='POST':
        serializer=UserSerializer(data=request.data)
        data={}
        if serializer.is_valid():
            account=serializer.save()
            data['response']="successfully registered new user"
            data['email'] = account.email
            data['username']=account.username
            token=Token.objects.get(user=account).key
            data['token']=token

        else:
            data=serializer.errors

        return Response(data)

