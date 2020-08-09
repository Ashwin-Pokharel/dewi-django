from django.db.models import Q
from rest_framework import viewsets, views
from .models import Courses, Classes, Documents, Assignment, StudentsAssignment
from .serializers import CoursesSerializer, ClassSerializer, DocumentSerializer, AssignmentSerializer, \
    StudentAssignmentsSerializer

from ibmUsers.models import Student, Teacher
from django.db import models
from courses.permissions import ClassesStudentPermission, ClassesTeacherPermission
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.http import FileResponse
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.request import Request
import json

assignment_choices = (('T', 'Test'), ('Q', 'Quiz'), ('H', 'Homework'))


class CoursesApiViewSet(viewsets.ModelViewSet):
    permission_classes = [ClassesTeacherPermission, ClassesStudentPermission]
    queryset = Courses.objects.all()
    serializer_class = CoursesSerializer


class ClassesApiViewSet(viewsets.ModelViewSet):
    permission_classes = [ClassesTeacherPermission, ClassesStudentPermission]
    queryset = Classes.objects.all()
    serializer_class = ClassSerializer


class DocumentApiViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Documents.objects.all()
    serializer_class = DocumentSerializer


class AssignmentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getCredits(request):
    user = request.user
    total_credits = 0
    try:
        student = Student.objects.get(user=user)
        classes = Classes.objects.filter(students__exact=student).all()
        for item in classes:
            total_credits += item.credit
        data = {'total_credits': total_credits}
        return Response(status=200, data=data)
    except Exception as e:
        print(e)
        return return_error_response_dict(500 , "internal server error")


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getAssignments(request):
    try:
        user = request.user
        class_id = request.data['class_id']
        weights = Classes.objects.get(class_id=class_id).weights.weights
        student = Student.objects.get(user=user)
        if student is None:
            return return_error_response_dict(400, "student Token not provided")
        assignments = StudentsAssignment.objects.get(Q(student=student, assignments__class_part=class_id))
        data_dict = {class_id: {}}
        for items in assignment_choices:
            data = data_dict.get(class_id)
            if data.get(items[0]) is None:
                data[items[0]] = {
                    "weight": weights[items[0]],
                    "assignments": AssignmentSerializer(assignments.assignments.filter(assignment_type=items[0]).all()
                                                        , many=True).data
                }
        return Response(status=200, data=data)
    except KeyError as e:
        print(e)
        return return_error_response_dict(400, "class_id not present in request")
    except Exception as e:
        print(e)
        return return_error_response_dict(500, "internal server error")


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getUserClasses(request):
    try:
        user = request.user
        student_found, student = check_student(user)
        if student_found:
            query = Classes.objects.filter(students=student)
            transform = ClassSerializer(query, many=True)
            data = transform.data
            return Response(status=200, data=data)
        teacher_found, teacher = check_teacher(user)
        if teacher_found:
            query = Classes.objects.filter(teachers=teacher)
            transform = ClassSerializer(query, many=True)
            data = transform.data
            return Response(status=200, data=data)
        else:
            return return_error_response_dict(400, 'user is neither teacher nor student')
    except Exception as e:
        return return_error_response_dict(500, 'internal server error')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getClassDocumentNames(request):
    try:
        data = request.data
        class_id = data['class_id']
        query = Documents.objects.filter(part_class=class_id)
        transform = DocumentSerializer(query, many=True)
        data = transform.data
        return Response(status=200, data=data)
    except KeyError as e:
        return return_error_response_dict(400, 'class_id is not present in request')
    except Exception as e:
        return return_error_response_dict(500, 'internal server error')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getDocument(request):
    try:
        data = request.data
        document_id = data['document_id']
        file = Documents.objects.get(document_id=document_id).document.open()
        return FileResponse(file, as_attachment=True, status=200)
    except ObjectDoesNotExist as e:
        return Response(status=400, data=json.dumps({}))


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getGPAScale():
    pass


def return_error_response_dict(status, error_message):
    return Response(status=status, data=json.dumps({'error': error_message}))


def check_student(user):
    try:
        student = Student.objects.get(user=user)
        return True, student
    except ObjectDoesNotExist as e:
        return False, None


def check_teacher(user):
    try:
        teacher = Teacher.objects.get(user=user)
        return True, teacher
    except ObjectDoesNotExist as e:
        return False, None
