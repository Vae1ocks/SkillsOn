from rest_framework import generics
from . import serializers
from .models import Course, Category

'''
class CoursesTitleOnlyListView(generics.ListAPIView):
    serializer_class = serializers.CourseTitleOnlySerializer
    queryset = Course.published.all()
'''

class CategoryListView(generics.ListAPIView):
    serializer_class = serializers.CategorySerializer
    queryset = Category.objects.all()