from djongo import models
import uuid
from ibmUsers.models import Student, Teacher
from ibmLMS import ibmCustomStorage
from django.utils.timezone import datetime
from ibmLMS import settings
import secrets
from jsonfield import JSONField
from django.db.models.signals import pre_delete, pre_save, post_save
from django.dispatch.dispatcher import receiver
from twilio.rest import Client
from decouple import config as envconfig

assignment_choices = (('T', 'Test'), ('Q', 'Quiz'), ('H', 'Homework'))


# Create your models here.

class GpaScale(models.Model):
    gpa_id = models.UUIDField(primary_key=True, blank=False, default=uuid.uuid4, editable=False)
    name=models.CharField(default="default gpa scale" , blank=False , max_length=300)
    gpa_scale = JSONField(blank=False, verbose_name='gpa_scale')

    def __str__(self):
        return self.name


class Weights(models.Model):
    weight_id = models.UUIDField(primary_key=True, blank=False, default=uuid.uuid4, editable=False)
    name = models.CharField(default="default weights scale", blank=False , max_length=300)
    weights = JSONField(blank=False , verbose_name='weights')

    def __str__(self):
        return self.name


class Courses(models.Model):
    course_id = models.UUIDField(primary_key=True, blank=False, default=uuid.uuid4, editable=False)
    course_code = models.PositiveSmallIntegerField(unique=True)
    name = models.CharField(blank=False, max_length=200, verbose_name="course name")
    start_date = models.DateTimeField(auto_now=False, verbose_name="start date")
    end_date = models.DateTimeField(auto_now=False, verbose_name="end date")

    def __str__(self):
        return self.name


class Classes(models.Model):
    class_id = models.UUIDField(primary_key=True, blank=False, default=uuid.uuid4, editable=False)
    credit = models.IntegerField(blank=False, verbose_name='credit')
    section_id = models.PositiveSmallIntegerField(verbose_name="class section ID", blank=False)
    start_time = models.TimeField(auto_now=False, blank=False, verbose_name="class start time")
    end_time = models.TimeField(auto_now=False, blank=False, verbose_name="class end time")
    course_part = models.ForeignKey(to='Courses', on_delete=models.CASCADE, verbose_name='Course part')
    grade_scale = models.ForeignKey(to='GpaScale', on_delete=models.CASCADE, verbose_name='Grade Scale' , blank=False)
    weights = models.ForeignKey(to='Weights', on_delete=models.CASCADE , verbose_name='Grade weights' , blank=False)
    students = models.ArrayReferenceField(
        to=Student,
        on_delete=models.CASCADE
    )
    teachers = models.ArrayReferenceField(
        to=Teacher,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return str(self.course_part) + '_' + str(self.section_id)


class Documents(models.Model):
    document_id = models.UUIDField(primary_key=True, blank=False, default=uuid.uuid4, editable=False)
    part_class = models.ForeignKey(to='Classes', on_delete=models.CASCADE)
    name = models.CharField(max_length=300, blank=False, verbose_name='document name')
    available_at = models.DateTimeField(verbose_name='document available start date')
    available_until = models.DateTimeField(verbose_name='document available end date')
    document = models.FileField(storage=ibmCustomStorage.IbmStorage())

    def __str__(self):
        return "{0}_{1}".format(str(self.part_class), self.name)

    def get_file_name(self):
        return self.document.name


class Assignment(models.Model):
    assignment_id = models.UUIDField(primary_key=True, blank=False, default=uuid.uuid4, editable=False)
    class_part = models.ForeignKey(to="Classes", on_delete=models.CASCADE)
    assignment_type = models.CharField(choices=assignment_choices, max_length=50)
    document = models.ForeignKey(to='Documents', blank=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=300, blank=False, verbose_name='assignment name')
    available_at = models.DateTimeField(verbose_name='assignment available start date', blank=True)
    available_end = models.DateTimeField(verbose_name='assignment available end date', blank=False)
    graded = models.BooleanField(verbose_name='graded', blank=False)
    total_points = models.IntegerField(blank=False, verbose_name='total points in assignment')
    points_earned = models.IntegerField(blank=True, verbose_name='total points earned in assignment')

    def __str__(self):
        return self.name


class StudentsAssignment(models.Model):
    student = models.OneToOneField(to=Student, on_delete=models.CASCADE, primary_key=True)
    assignments = models.ArrayReferenceField(
        to=Assignment,
        on_delete=models.CASCADE,
        blank=True
    )


@receiver(post_save, sender=Assignment)
def assignment_addition(sender, instance, **kwargs):
    part_class = instance.class_part
    for students in part_class.students.all():
        assign = StudentsAssignment.objects.get_or_create(student=students)
        if assign[1]:
            assign[0].save()
        assign[0].assignments.add(instance)


@receiver(post_save, sender=Assignment)
def assignment_notification(sender , instance , **kwargs):
    client = Client(envconfig('TWILIO_ACCOUNT_SID'), envconfig('TWILIO_AUTH_TOKEN'))
    class_part = instance.class_part
    available_date = instance.available_start.strftime("%b/%d/%y %I:%M:%S %p")
    due_data = instance.available_end.strftime("%b/%d/%y %I:%M:%S %p")
    message = "New assignment! from: {0}\n\t- Name: {1}\n\t- Available on: {2}\n\t-Due date: {3}  \n Good Luck!! You " \
              "got this! 😀".format(str(class_part) , instance.name , available_date , due_data)
    for student in class_part.students.all():
        phone = str(student.user.phone_number)
        sent = client.messages.create(
            body=message,
            from_='+12027653536',
            to=phone)


@receiver(pre_delete, sender=Documents)
def document_delete(sender, instance, **kwargs):
    instance.document.delete(instance.document.name)
