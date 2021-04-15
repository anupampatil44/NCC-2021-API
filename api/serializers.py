from rest_framework import serializers
from django.contrib.auth.models import User

# User Serializer
from data.models import Userdata,Question


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email')


class LeaderboardSerializer(serializers.ModelSerializer):
    username=UserSerializer(read_only=True,)
    class Meta:
        model=Userdata
        fields=('username','totalScore')

# Register Serializer
class AccountSerializer(serializers.ModelSerializer):

    class RegisterSerializer(serializers.ModelSerializer):
        class Meta:
            model = Userdata
            exclude=['username','totalScore','correctly_solved','attempted']


    profile=RegisterSerializer()
    class Meta:
        model=User
        exclude = ['last_login', 'is_superuser', 'is_staff', 'date_joined', 'is_active', 'groups', 'user_permissions']
        # extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        print("validated data:\n",validated_data)
        profile_data = validated_data.pop("profile")
        useri = User.objects.create_user(**validated_data)
        Userdata.objects.create(username=useri,**profile_data)
        return useri


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ('question_title', 'question_desc', 'correct_attempts', 'total_attempts', 'max_marks')

class Codingpageserializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ('question_title', 'question_desc', 'constraints', 'explanation', 'iformat','oformat','sampleInput','sampleOutput')
