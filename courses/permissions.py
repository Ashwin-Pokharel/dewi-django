from rest_framework.permissions import BasePermission
from ibmUsers.models import Teacher , Student


class ClassesTeacherPermission(BasePermission):
    def has_permission(self, request, view):
        permissions = ['GET', 'POST', 'DELETE', 'PUT', 'PATCH']
        if request.auth is None:
            return False
        else:
            user = request.user
            teacher_obj = Teacher.objects.get(user=user)
            if teacher_obj is None or request.method not in permissions:
                return False
            else:
                return True


class ClassesStudentPermission(BasePermission):

    def has_permission(self, request, view):
        permissions = ['GET']
        if request.auth is None:
            return False
        else:
            user = request.user
            student_obj = Student.objects.get(user=user)
            if student_obj is None or request.method not in permissions:
                return False
            else:
                return True
