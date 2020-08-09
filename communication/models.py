from djongo import models
from courses.models import Classes
from ibmUsers.models import Student
import datetime


class Notification(models.Model):
    content = models.CharField(max_length=1000, blank=False)
    class_part = models.ForeignKey(to=Classes, blank=False , on_delete=models.CASCADE)
    sent_date = models.DateTimeField(default=datetime)

# Create your models here.
