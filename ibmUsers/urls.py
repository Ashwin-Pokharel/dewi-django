from django.contrib import admin
from django.urls import path , include
from django.conf.urls import url
import ibmUsers.urls
from rest_framework.authtoken.views import obtain_auth_token
from .views import HelloWorld
import djoser


urlpatterns = [
    url(r'^hello' , HelloWorld.as_view()),
    url(r'^auth/' ,include('djoser.urls')),
    url(r'^auth/' ,include('djoser.urls.authtoken'))
]