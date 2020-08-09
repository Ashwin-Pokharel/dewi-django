from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from ibmUsers.models import User, Student
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from twilio.rest import Client
from decouple import config as envconfig
from django.db.models.signals import pre_delete, pre_save, post_save
from django.dispatch.dispatcher import receiver

# Create your views here.
client = Client(envconfig('TWILIO_ACCOUNT_SID'), envconfig('TWILIO_AUTH_TOKEN'))


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def sendMessage(request):
    user = request.user
    phone = str(Student.objects.get(user=user).user.phone_number)
    message = client.messages.create(
        body="your'e doing great :-)!",
        from_='+12027653536',
        to=phone
    )
    return Response(status=200, data="text sent")


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def receiveInput(request):
    print(request.data)
    return Response(status=200, data="received data")
