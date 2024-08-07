from rest_framework.generics import ListAPIView, \
    CreateAPIView, UpdateAPIView, RetrieveUpdateDestroyAPIView, DestroyAPIView, GenericAPIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from rest_framework.exceptions import NotFound, ValidationError, ParseError
from django.db.models import Func, IntegerField
from django.db.models.functions import Lower
from . import serializers
from .models import Course, Category, Lesson, CourseComment, LessonComment
from .permissions import IsAuthor, IsStudent, IsAuthorOrStudent
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes, OpenApiResponse, inline_serializer
import requests
import json


class CategoryListView(ListAPIView):
    serializer_class = serializers.CategorySerializer
    queryset = Category.objects.all()


class CourseOverviewList(GenericAPIView):
    serializer_class = serializers.CourseSerializer # не он, просто для drf_spectacular
    @extend_schema(
            description='Для просмотра курсов в случае отсутствия параметров фильтрации/сортировки. '
                        'В данном случае количество курсов для каждой категории будет ограничено 8. '
                        'Количество "most_popular" - до 15.',
            responses={
                200: OpenApiResponse(
                    response=inline_serializer(
                        name='Overview Serializer',
                        fields={
                            'most_popular': serializers.CourseSerializer(many=True),
                            'some_category_title': serializers.CourseSerializer(many=True),
                            'some_other_category_title': serializers.CourseSerializer(many=True)
                        }
                    )
                )
            }
    )
    def get(self, request, *args, **kwargs):
        result = {}
        categories_liked = []

        most_liked = Course.published.all().order_by('-rating')[:60]
        most_popular = Course.objects.annotate(student_count=Func(
            'students', function='jsonb_array_length', output_field=IntegerField()
        )).filter(id__in=most_liked.values('id')).order_by('-student_count')[:15]
        most_popular_ids = most_popular.values('id')
        most_popular_data = serializers.CourseSerializer(most_popular, many=True).data
        result['most_popular'] = most_popular_data

        if self.request.user.is_authenticated:
            base_uri = self.request.build_absolute_uri('/')
            relative_url = f'users/user/{self.request.user.id}/personal-preferences/'
            url = f'{base_uri}{relative_url}'
            response = requests.get(url)
            if response.status_code == 200: # [{'id': 5, 'title': 'title}, {'id': 6, 'title': 'titttle'}]
                categories_liked = response.json()
                categories_ids = [category['id'] for category in categories_liked]
                categories_liked = Category.objects.filter(id__in=categories_ids)
                for category in categories_liked:
                    rec_queryset = Course.published.filter(category=category).exclude(
                        id__in=most_popular_ids
                    ).order_by('-rating')[:8]
                    data = serializers.CourseSerializer(rec_queryset, many=True).data
                    result[category.title] = data
        categories = Category.objects.exclude(id__in=categories_liked).only('id', 'title')
        for category in categories:
            queryset = Course.published.filter(category=category).exclude(
                id__in=most_popular_ids
            ).order_by('-rating')[:8]
            data = serializers.CourseSerializer(queryset, many=True).data
            result[category.title] = data
        return Response(result, status.HTTP_200_OK)
    


class CourseViewSet(ModelViewSet):
    def get_queryset(self):
        if self.action == 'list':
            # if self.request.user.is_authenticated:
            #     base_uri = self.request.build_absolute_uri('/')
            #     relative_url = f'users/user/{self.request.user.id}/personal-preferences/'
            #     url = f'{base_uri}{relative_url}'
            #     response = requests.get(url)
            #     if response.status_code == 200:
            #         categories_liked = response.json()
            #         categories_ids = [category['id'] for category in categories_liked]
            #         queryset = Course.published.all().annotate(
            #             is_liked=Case(
            #                 When(category_id__in=categories_ids, then=Value(1)),
            #                 default=Value(0),
            #                 output_field=IntegerField()
            #             )
            #         ).order_by('-is_liked', '-price', '-students_count')
            #     else: queryset = Course.published.all()
            # else: queryset = Course.published.all()
            # title = self.request.query_params.get('title', None)
            # if title:
            #     queryset = queryset.filter(title__icontains=title)
            # return queryset
            
            category = self.request.query_params.get('category')
            title = self.request.query_params.get('title')
            order_by = self.request.query_params.get('order_by')
            allowable_price = self.request.query_params.get('price')
            level = self.request.query_params.get('level')

            queryset = Course.published.all()

            if category:
                cat_titles = [title.strip().lower() for title in category.split(',')]
                categories = Category.objects.annotate(lower_title=Lower('title')).filter(
                    lower_title__in=cat_titles
                )
                queryset = queryset.filter(category__in=categories)

            if title:
                queryset = queryset.filter(title__icontains=title)

            if level:
                queryset = queryset.filter(level=level)

            if allowable_price:
                try:
                    min_val, max_val = map(float, allowable_price.split(';'))
                    queryset = queryset.filter(price__gte=min_val, price__lte=max_val)
                except ValueError:
                    raise ParseError('Параметр "price" должен быть в формате "min;max"')
            
            if order_by:
                if order_by == 'price-high-to-low':
                    queryset = queryset.order_by('-price')
                elif order_by == 'price-low-to-high':
                    queryset = queryset.order_by('price')
                elif order_by == 'rating-high-to-low':
                    queryset = queryset.order_by('-rating')

            if not category and not title and not allowable_price and not order_by and not level:
                raise ParseError('Необходимы параметры фильтрации и/или сортировки')

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

    @extend_schema(
            description='Создание курса, "category" - название категории, "draft" - метка, хочет ли автор '
                        'опубликовать курс или курс ещё подлежит редактированию, доступные варианты для '
                        '"level": "high", "medium", "low"'
    )
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
        base_url = self.request.build_absolute_uri('/')
        relative_url = f'users/user/{request.user.id}/personal-info/'
        url = f'{base_url}{relative_url}'

        response = requests.get(url)
        if response.status_code == 200:
            response_data = response.json()
            first_name = response_data['first_name']
            last_name = response_data['last_name']
            author_image = response_data['profile_picture']
            serializer = self.get_serializer(data=data, context={'request': request,
                                                                 'first_name': first_name,
                                                                 'last_name': last_name,
                                                                 'author_image': author_image})
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def perform_update(self, serializer):
        if len(serializer.validated_data) == 1 and 'price' in serializer.validated_data:
            serializer.save()
        else:
            serializer.save(moderated=False)

    def retrieve(self, request, *args, **kwargs):
        course = self.get_object()
        if (not course.moderated or course.draft) and (course.author != request.user.id):
            return Response({'detail': 'Курс не найден'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(course)
        return Response(serializer.data)
    
    @extend_schema(
            description='Для фильтрации или сортировки товаров. Возвращает простой список товаров'
                        'согласно параметрам фильтрации/сортировки. В случае отсутствия хотя бы 1 '
                        'параметра, возвращает "Необходимы параметры фильтрации и/или сортировки".',
            parameters=[
                OpenApiParameter(name='title', description='Параметр для фильтрации по названию товаров',
                                required=False, type=OpenApiTypes.STR),
                OpenApiParameter(name='allowable_price', description='Параметр для фильтрации по цене в формате min;max',
                                required=False, type=OpenApiTypes.INT),
                OpenApiParameter(name='level', description='Для фильтрации по уровню',
                                required=False, type=OpenApiTypes.STR),
                OpenApiParameter(name='category', description='''Для фильтрации по товаров по категории,
                                возможно указание как 1 категории, так и нескольких в формате cat_title1, 
                                cat_title2. Пробел между значениями не учитывается. Регистр не учитывается
                                ''', required=False, type=OpenApiTypes.STR),
                OpenApiParameter(name='order_by', description='''Для сортировки товаров. Возможные значения: 
                            price-high-to-low, price-low-to-high, rating-high-to-low''',
                            required=False, type=OpenApiTypes.STR)
            ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    def perform_destroy(self, instance):
        if len(instance.students) != 0:
            return Response({'detail': 'more than 0 students'}, status=status.HTTP_403_FORBIDDEN)
        instance.delete()


class UserCourseListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.UserCourseSerializer

    def get_queryset(self):
        return Course.published.filter(students__contains=self.request.user.id)
    
    @extend_schema(description='Для просмотра купленных и созданных курсов. "is_owner" - булево значение, '
                                'показывающее, является ли данный курс созданным данным пользователем или '
                                'этот курс был куплен пользователем. Поле "lessons_seen" возвращает '
                                'строку в формате: "xx%" т.е: "40%", "50%", "90%", т.е служит для отображения '
                                'прогресса по прохождению курса. Для курсов, которые были выложены тем же '
                                'пользователем, который сейчас находится на этом ендпоните (т.е "is_owner": True) '
                                'данное поле примет значение "N/A (или если пользователь не является студентом курса)", '
                                'если у курса всего по какой-то причине 0 уроков, но при этом у курса есть студенты '
                                'и студент сейчас просматривает данный ендпоинт, то для этого поля будет значение "0%"')
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


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
    
    @extend_schema(
            description=""" "reply_comments" содержит массив json-объектов, которые ссылаются на этот
                        комментарий, т.е те комментарии, которые являются ответом на текущий комментарий.
                        Содержит None в случае, если такие комментарии отсутствуют.
                        "is_note" - булево значение, регулирующее, является ли комментарий комментарием, или же
                        это личная заметка пользователя, например, какое-то определение, выписанное из самого урока,
                        т.е не предназначенное для других пользователей.
                        """
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    
class CourseCommentCreateView(CreateAPIView):
    serializer_class = serializers.CourseCommentSerializer
    permission_classes = [IsAuthorOrStudent]
    queryset = Course.published.all()
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request

        base_url = self.request.build_absolute_uri('/')
        relative_url = f'users/user/{self.request.user.id}/personal-info/'
        url = f'{base_url}{relative_url}'
        response = requests.get(url)

        if response.status_code == 200:
            response_data = response.json()
            first_name = response_data['first_name']
            last_name = response_data['last_name']
            author_image = response_data['profile_picture']
            context['first_name'] = first_name
            context['last_name'] = last_name
            context['author_image'] = author_image
        else:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
        base_url = self.request.build_absolute_uri('/')
        relative_url = f'users/user/{self.request.user.id}/personal-info/'
        url = f'{base_url}{relative_url}'
        response = requests.get(url)
        
        if response.status_code == 200:
            response_data = response.json()
            first_name = response_data['first_name']
            last_name = response_data['last_name']
            author_image = response_data['profile_picture']
            context['first_name'] = first_name
            context['last_name'] = last_name
            context['author_image'] = author_image
        else:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return context
    

class LessonCommentUpdateView(UpdateAPIView):
    serializer_class = serializers.LessonCommentSerializer
    permission_classes = [IsAuthor]
    queryset = LessonComment.objects.all()


class LessonCommentDestroyView(DestroyAPIView):
    permission_classes = [IsAuthor]
    queryset = LessonComment.objects.all()