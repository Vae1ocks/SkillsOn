from rest_framework import serializers
from .models import JSONLength, Category, Course


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['title']


class CourseSerializer(serializers.ModelSerializer):
    students_count = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ['title', 'owner_id', 'students_count', 'description', 'created']

    def get_students_count(self, obj):
        return JSONLength(obj.students_ids)
    

class CourseTitleOnlySerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['title']