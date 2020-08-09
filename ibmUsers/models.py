from django.contrib.auth.models import AbstractBaseUser
from djongo import models
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import PermissionsMixin
from django.utils import timezone
from ibmUsers.manager import UserManager
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, help_text='Email Address', blank=False, primary_key=True)
    first_name = models.CharField(max_length=50, help_text='First Name', blank=False)
    last_name = models.CharField(max_length=50, help_text='Last Name', blank=False)
    phone_number = PhoneNumberField(blank=False, help_text='Phone Number')
    is_teacher = models.BooleanField(default=False, blank=False)
    is_school_admin = models.BooleanField(default=False, blank=True)
    date_joined = models.DateTimeField(default=timezone.now)
    last_active = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False, blank=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'phone_number', 'is_teacher']

    class Meta:
        app_label = 'ibmUsers'
        verbose_name = 'user'
        verbose_name_plural = 'users'

    def __str__(self):
        return self.first_name + ' ' + self.last_name

    def get_email(self):
        return self.email

    def get_first_name(self):
        return self.first_name

    def get_last_name(self):
        return self.last_name

    def get_phone_number(self):
        return self.phone_number

    def get_full_name(self):
        return "{0} {1}".format(self.first_name, self.last_name)

    def get_short_name(self):
        return self.first_name

    def get_last_active(self):
        return self.last_active

    def get_token(self):
        return Token.objects.get(user=self)

    def get_is_teacher(self):
        return self.is_teacher

    def get_is_admin(self):
        return self.is_school_admin


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def determine_user_type(sender, instance=None, created=False, **kwargs):
    if created:
        if instance.is_teacher:
            Teacher.objects.create(user=instance)
        else:
            Student.objects.create(user=instance)


class Student(models.Model):
    user = models.ForeignKey(User, blank=False, on_delete=models.CASCADE)
    initial_login = models.BooleanField(default=True, blank=True)

    def __str__(self):
        return 'Student({0})'.format(str(self.user))


class Teacher(models.Model):
    user = models.ForeignKey(User, blank=False, on_delete=models.CASCADE)

    def __str__(self):
        return 'Teacher({0})'.format(str(self.user))
