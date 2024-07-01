from rest_framework.generics import ListAPIView, \
    CreateAPIView, UpdateAPIView, RetrieveUpdateDestroyAPIView, DestroyAPIView
from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from rest_framework.exceptions import NotFound, ValidationError
from . import serializers
from .models import Course, Category, Lesson, CourseComment, LessonComment
from .permissions import IsAuthor, IsStudent, IsAuthorOrStudent


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
        if course.draft and course.author != self.request.user.email:
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
            return Course.published.all()
        return Course.objects.all()
    
    def get_object(self):
        if self.action == 'list':
            return super().get_object()
        obj = super().get_object()
        if not obj.moderated and obj.author != self.request.user.email:
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

        serializer = self.get_serializer(data=data)
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
        if course.draft and course.author != request.author.email:
            return Response({'detail': 'course_not_found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(course)
        return Response(serializer.data)
    
    def perform_destroy(self, instance):
        if len(instance.students) != 0:
            return Response({'detail': 'more than 0 students'}, status=status.HTTP_403_FORBIDDEN)
        instance.delete()


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
        return Lesson.objects.filter(course__author=self.request.user.email)
    
    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [IsAuthorOrStudent()]
        return [IsAuthor()]
    
    def perform_update(self, serializer):
        serializer.save(moderated=False)
    
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