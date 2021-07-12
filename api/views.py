import os
import datetime
from tokenize import Token
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

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

from .serializers import UserSerializer, AccountSerializer, QuestionSerializer,Codingpageserializer,LeaderboardSerializer,SubmissionsSerializer
from data.models import Question,Userdata,Submission,User
from rest_framework.pagination import PageNumberPagination
from collections import OrderedDict
# @api_view(['POST',])

path_users_code = 'code_related/usersCode/'

# variables used for timer
start_time = 0
end_time = 0
duration = 0
flag = False
start = datetime.datetime(2021, 1, 1, 0, 0)

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


class LeaderboardPage(APIView,PageNumberPagination):
    permission_classes = (IsAuthenticated,)

    def get(self,request):
        l=[]
        question_count=Question.objects.all().count()
        print("question count",question_count)
        query=Userdata.objects.order_by('-totalScore','latest_ac_time')
        pageno = int(request.GET.get('page','1'))
        paginator = Paginator(query, 10)
        page_obj=paginator.get_page(pageno)
        page_range = paginator.page_range

        rankcount=1
        ranklist=[]
        for coder in query.iterator():
            usert=User.objects.get(username=coder)
            ranklist.append(rankcount)
            rankcount+=1
            temp=[]
            for i in range(1,question_count+1):
                que = Question.objects.get(pk=i)
                if( Submission.objects.filter(question_id_fk=que,user_id_fk=usert).exists()):
                    maxs=Submission.objects.filter(question_id_fk=que,user_id_fk=usert).order_by('-score')[0].score
                    temp.append(maxs)
                else:
                    temp.append(0)
            l.append(temp)

        serializer=LeaderboardSerializer(page_obj,many=True,context={'page_range':list(page_range)})
        for i in range(len(serializer.data)):
            serializer.data[i]["scorelist"]=l[i]
            serializer.data[i]["rank"] = ranklist[i+(pageno-1)*10]

        return Response(serializer.data)

class SubmissionsPage(APIView):
    permission_classes = (IsAuthenticated,)
    def post(self,request):
        user=request.user
        data=request.data
        query=Submission.objects.filter(user_id_fk=user,question_id_fk=data["qno"]).order_by('submission_time')
        serializer=SubmissionsSerializer(query,many=True)
        return Response(serializer.data)

class Userstats(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user=Userdata.objects.get(username=request.user)
        #calculation of rank:
        query = Userdata.objects.order_by('-totalScore', 'latest_ac_time')
        question_count = Question.objects.all().count()
        current_rank = 1
        scorelist=[]
        for user1 in query:
            print("current rank:",current_rank)
            print("user",user1.username)
            if(str(user1.username)!=str(request.user.username)):
                current_rank += 1
            if str(user1.username) == str(request.user.username):
                usert = User.objects.get(username=user1)
                for i in range(1, question_count + 1):
                    que = Question.objects.get(pk=i)
                    if (Submission.objects.filter(question_id_fk=que, user_id_fk=usert).exists()):
                        maxs = Submission.objects.filter(question_id_fk=que, user_id_fk=usert).order_by('-score')[
                            0].score
                        scorelist.append(maxs)
                    else:
                        scorelist.append(0)
                break

        data={
            "username":request.user.username,
            "rank":current_rank,
            "totalScore":user.totalScore,
            "correctly_solved":user.correctly_solved,
            "attempted":user.attempted,
            "scorelist":scorelist,
        }

        return Response(data)

class loadbuffer(APIView):
    permission_classes = (IsAuthenticated,)
    def post(self,request):
        data=request.data
        qno=data["qno"]
        code={}
        if(Submission.objects.filter(user_id_fk=request.user,question_id_fk=qno).exists()):
            required=Submission.objects.filter(user_id_fk=request.user,question_id_fk=qno).order_by('-submission_time')[0]
            code["code"]=required.code
            code["lang"]=required.language

        else:
            code["code"]="No submission for this question has been made yet."
            code["lang"] ="NA"

        return Response(code)


class Timer(APIView):
    # permission_classes = [IsAuthenticated]

    @staticmethod
    def remaining_time():
        time = datetime.datetime.now()
        print(time)
        now = (time.hour * 60 * 60) + (time.minute * 60) + time.second
        if now < end_time:
            time_left = end_time - now
            print(time_left)
            return time_left
        else:
            print("now",now)
            print("end",end_time)
            return 0



    def get(self, request):
        if Timer.remaining_time() != 0:
            val = {'status': 'Remaining time is {}'.format(self.remaining_time())}
            return Response(val, status=201)
        val = {'status': 'Time is up!'}
        return Response(val, status=201)