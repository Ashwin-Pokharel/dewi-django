from django.contrib import admin
from django.urls import path , include
from django.conf.urls import url
from rest_framework import routers
from .views import sendMessage ,receiveInput

urlpatterns = [
    path('send_text' , sendMessage),
    path('get_initial_data', receiveInput)
]