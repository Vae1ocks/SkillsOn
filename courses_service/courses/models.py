from django.db import models
from django.db.models import Func
from django.db.models import Count
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth import get_user_model


class JSONLength(Func):
    function = 'jsonb_array_length'
    template = '%(function)s(%(expressions)s)'


class Category(models.Model):
    title = models.CharField(max_length=150, unique=True)
    slug = models.CharField(max_length=150, unique=True) # slug пока не надо, мб удалить в будущем


class CourseManager(models.Manager):
    def get_most_popular(self):
        return self.get_queryset().filter(draft=False).annotate(
            students_count=JSONLength('student_ids')).order_by('-price', '-students_count')


class Course(models.Model):
    owner = models.EmailField()
    students_ids = models.JSONField(default=list)
    category = models.ForeignKey(Category,
                                 related_name='courses',
                                 on_delete=models.CASCADE) # В будущем заменить на models.SET_DEFAULT

    title = models.CharField(max_length=200)
    slug = models.CharField(max_length=200)
    description = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    draft = models.BooleanField(default=True)

    published = CourseManager() # Миграций нет
    objects = models.Manager()

    def __str__(self):
        return self.title


class Lesson(models.Model):
    course = models.ForeignKey(Course,
                               on_delete=models.CASCADE,
                               related_name='lessons')
    
    title = models.CharField(max_length=200)
    slug = models.CharField(max_length=200)
    body = models.TextField()