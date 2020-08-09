from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView , HttpResponseBase

# Create your views here.

class HelloWorld(APIView):
    def get(self , request):
        content = {'Hello':'World'}
        return  Response(content)

