from rest_framework.generics import ListAPIView, \
    CreateAPIView, UpdateAPIView, RetrieveUpdateDestroyAPIView, DestroyAPIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from rest_framework.exceptions import NotFound, ValidationError
from django.db.models import Case, When, Value, IntegerField
from . import serializers
from .models import Course, Category, Lesson, CourseComment, LessonComment
from .permissions import IsAuthor, IsStudent, IsAuthorOrStudent
import requests
import json


class CategoryListView(ListAPIView):
    serializer_class = serializers.CategorySerializer
    queryset = Category.objects.all()

'''
class CourseListView(ListAPIView):
    serializer_class = serializers.CourseSerializer
    queryset = Course.published.all()


class CourseDetailView(RetrieveAPIView):
    serializer_class = serializers.CourseDetailSerializer
    queryset = Course.objects.all()

    def get_object(self):
        course = super().get_object()
        if course.draft and course.author != self.request.user.id:
            return Response({'detail': 'course not found'}, status=status.HTTP_404_NOT_FOUND)
        return course
    

class CourseCreateView(CreateAPIView):
    serializer_class = serializers.CourseCreateSerializer


class CourseUpdateView(UpdateAPIView):
    serializer_class = serializers.CourseCreateSerializer

    def perform_create(self, serializer):
        serializer.save(moderated=False)
'''


class CourseViewSet(ModelViewSet):
    def get_queryset(self):
        if self.action == 'list':
            if self.request.user.is_authenticated:
                base_uri = self.request.build_absolute_uri('/')
                relative_url = f'users/user/{self.request.user.id}/personal-preferences/'
                url = f'{base_uri}{relative_url}'
                response = requests.get(url)
                if response.status_code == 200:
                    categories_liked = response.json()
                    categories_ids = [category['id'] for category in categories_liked]
                    queryset = Course.published.all().annotate(
                        is_liked=Case(
                            When(category_id__in=categories_ids, then=Value(1)),
                            default=Value(0),
                            output_field=IntegerField()
                        )
                    ).order_by('-is_liked', '-price', '-students_count')
                else: queryset = Course.published.all()
            else: queryset = Course.published.all()
            title = self.request.query_params.get('title', None)
            if title:
                queryset = queryset.filter(title__icontains=title)
            return queryset
        return Course.objects.all()
    
    def get_object(self):
        if self.action == 'list':
            return super().get_object()
        obj = super().get_object()
        if not obj.moderated and obj.author != self.request.user.id:
            raise NotFound(detail='Course not found')
        return obj

    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.CourseSerializer
        if self.action == 'retrieve':
            return serializers.CourseDetailSerializer
        if self.action in ['create', 'update', 'partial_update']:
            return serializers.CourseCreateSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated()]
        if self.action in ['update', 'partial_update']:
            return [IsAuthor()]
        if self.action == 'get':
            return [IsAuthorOrStudent()]
        return []

    def create(self, request, *args, **kwargs):
        data = request.data
        data['moderated'] = False
        if 'category' not in data:
            raise ValidationError(detail='No category selected')
        
        category_title = data.pop('category')
        try:
            category = Category.objects.get(title=category_title)
        except Category.DoesNotExist:
            raise ValidationError(detail='Incorrect category')
        
        data['category'] = category.id

        serializer = self.get_serializer(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_update(self, serializer):
        if len(serializer.validated_data) == 1 and 'price' in serializer.validated_data:
            serializer.save()
        else:
            serializer.save(moderated=False)

    def retrieve(self, request, *args, **kwargs):
        course = self.get_object()
        if (not course.moderated or course.draft) and (course.author != request.user.id):
            return Response({'detail': 'course_not_found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(course)
        return Response(serializer.data)
    
    def lidst(self, request, *args, **kwargs):
        self.list
    
    def perform_destroy(self, instance):
        if len(instance.students) != 0:
            return Response({'detail': 'more than 0 students'}, status=status.HTTP_403_FORBIDDEN)
        instance.delete()


class UserCourseListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.UserCourseSerializer

    def get_queryset(self):
        return Course.published.filter(students__contains=self.request.user.id)


class LessonCreateView(CreateAPIView):
    serializer_class = serializers.LessonSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(moderated=False)    


class LessonViews(RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.LessonSerializer

    def get_queryset(self):
        if self.request.method in SAFE_METHODS:
            return Lesson.published.all()
        return Lesson.objects.filter(course__author=self.request.user.id)
    
    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [IsAuthorOrStudent()]
        return [IsAuthor()]
    
    def perform_update(self, serializer):
        serializer.save(moderated=False)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        user_id = request.user.id
        if user_id not in instance.users_seen:
            instance.users_seen.append(user_id)
            instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    
class CourseCommentCreateView(CreateAPIView):
    serializer_class = serializers.CourseCommentSerializer
    permission_classes = [IsAuthorOrStudent]
    queryset = Course.published.all()
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    

class CourseCommentUpdateView(UpdateAPIView):
    serializer_class = serializers.CourseCommentSerializer
    permission_classes = [IsAuthor]
    queryset = CourseComment.objects.all()


class CourseCommentDestroyView(DestroyAPIView):
    permission_classes = [IsAuthor]
    queryset = CourseComment.objects.all()


class LessonCommentCreateView(CreateAPIView):
    serializer_class = serializers.LessonCommentSerializer
    permission_classes = [IsStudent]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request    
        return context
    

class LessonCommentUpdateView(UpdateAPIView):
    serializer_class = serializers.LessonCommentSerializer
    permission_classes = [IsAuthor]
    queryset = LessonComment.objects.all()


class LessonCommentDestroyView(DestroyAPIView):
    permission_classes = [IsAuthor]
    queryset = LessonComment.objects.all()