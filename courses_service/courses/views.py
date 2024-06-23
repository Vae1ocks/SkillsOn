from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework import status
from rest_framework.response import Response
from . import serializers
from .models import Course, Category


class CategoryListView(ListAPIView):
    serializer_class = serializers.CategorySerializer
    queryset = Category.objects.all()


class CoursesListView(ListAPIView):
    serializer_class = serializers.CourseSerializer
    queryset = Course.published.all()


class CourseDetailView(RetrieveAPIView):
    serializer_class = serializers.CourseDetailSerializer
    queryset = Course.objects.all()

    def get_object(self):
        course = super().get_object()
        if course.draft and course.owner != self.request.user.email:
            return Response({'detail': 'course not found'}, status=status.HTTP_404_NOT_FOUND)
        return course