import os
from tokenize import Token
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required

from rest_framework import permissions, generics
from rest_framework.authentication import BasicAuthentication
from rest_framework.authtoken.serializers import AuthTokenSerializer
from knox.views import LoginView as KnoxLoginView
from rest_framework import permissions
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from knox.models import AuthToken
from rest_framework.views import APIView

from .serializers import UserSerializer, AccountSerializer, QuestionSerializer,Codingpageserializer,LeaderboardSerializer
from data.models import Question,Userdata


# @api_view(['POST',])

path_users_code = 'code_related/usersCode/'

class RegisterAPI(generics.GenericAPIView):
    serializer_class = AccountSerializer
    permission_classes = (permissions.AllowAny,)
    def post(self, request, *args, **kwargs):
        print("data:\n",request.data)
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            os.system("mkdir {}/{}".format(path_users_code,request.data["username"]))
            return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "token": AuthToken.objects.create(user)[1]
            })

        else:
            data = serializer.errors   #{"exception":str(e)}
            return Response(data)




class LoginAPI(KnoxLoginView):
    permission_classes = (permissions.AllowAny,)
    # authentication_classes = [BasicAuthentication]

    def post(self, request, format=None):
        serializer = AuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        return super(LoginAPI, self).post(request, format=None)






class questionhub(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self, request, format=None):

        if request.method == 'GET':
            questions = Question.objects.all()
            serializer=QuestionSerializer(questions,many=True)
            return Response(serializer.data)


class codingpage(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self,request,format=None):

        if request.method == 'GET':
            questions = Question.objects.all()
            serializer=Codingpageserializer(questions,many=True)
            return Response(serializer.data)

@api_view(['GET'])
def current_user(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)

@api_view(["GET"])
def leaderboard(request):
    query=Userdata.objects.order_by('-totalScore')
    seriaizer=LeaderboardSerializer(query,many=True)
    return Response(seriaizer.data)