from abc import ABC, ABCMeta

from rest_framework.serializers import ModelSerializer, Serializer, HyperlinkedModelSerializer
from rest_framework import serializers
from .models import Courses, Classes, Documents, GpaScale, Assignment, StudentsAssignment
from ibmUsers.serializers import teacherSerializer, studentSerializer


class CoursesSerializer(ModelSerializer):
    class Meta:
        model = Courses
        fields = ['course_id', 'course_code', 'name', 'start_date', 'end_date']


class GPAScaleSerializer(ModelSerializer):
    class Meta:
        model = GpaScale
        fields = ['gpa_scale']


class ClassSerializer(ModelSerializer):
    course_part = CoursesSerializer()
    grade_scale = GPAScaleSerializer()

    class Meta:
        model = Classes
        fields = ['class_id', 'credit', 'section_id', 'start_time', 'end_time', 'course_part', 'grade_scale', ]


class DocumentSerializer(ModelSerializer):

    class Meta:
        model = Documents
        fields = ['document_id', 'part_class', 'name', 'available_at', 'available_until']


class AssignmentSerializer(ModelSerializer):
    document = DocumentSerializer()
    graded = serializers.BooleanField()

    class Meta:
        model = Assignment
        fields = ['assignment_id', 'graded', 'name', 'document', 'available_at', 'available_end', 'total_points',
                  'points_earned' , 'document']


class StudentAssignmentsSerializer(ModelSerializer):
    assignments = AssignmentSerializer(many=True, read_only=True)

    class Meta:
        model = StudentsAssignment
        fields = ['assignments']
