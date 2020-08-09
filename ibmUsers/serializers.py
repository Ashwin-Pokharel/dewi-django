from rest_framework.serializers import ModelSerializer
from rest_framework.serializers import Serializer
from rest_framework import serializers
from .models import Teacher, Student, User


class userSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'phone_number', 'last_active', 'is_teacher']


class studentSerializer(Serializer):
    user = userSerializer()


class teacherSerializer(Serializer):
    user = userSerializer()
