from tokenize import Token
from django.contrib.auth import login

from rest_framework import permissions, generics
from rest_framework.authtoken.serializers import AuthTokenSerializer
from knox.views import LoginView as KnoxLoginView
from rest_framework import permissions
from rest_framework.decorators import api_view
from rest_framework.response import Response

from knox.models import AuthToken
from .serializers import UserSerializer, AccountSerializer, QuestionSerializer,Codingpageserializer
from data.models import Question


# @api_view(['POST',])



class RegisterAPI(generics.GenericAPIView):
    serializer_class = AccountSerializer

    def post(self, request, *args, **kwargs):
        print("data:\n",request.data)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = serializer.save()
            return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "token": AuthToken.objects.create(user)[1]
            })

        except Exception as e:
            data = serializer.errors   #{"exception":str(e)}
            return Response(data)




class LoginAPI(KnoxLoginView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        serializer = AuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        return super(LoginAPI, self).post(request, format=None)

@api_view(('GET',))
def questionhub(request):
    if request.method == 'GET':
        questions = Question.objects.all()
        serializer=QuestionSerializer(questions,many=True)
        return Response(serializer.data)

@api_view(('GET',))
def codingpage(request):
    if request.method == 'GET':
        questions = Question.objects.all()
        serializer=Codingpageserializer(questions,many=True)
        return Response(serializer.data)