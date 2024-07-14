from django.db import models
from django.db.models import Func, F
from django.db.models import Count
from django.utils import timezone
from django.urls import reverse
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from .fields import OrderField
from django.utils.text import slugify
from unidecode import unidecode


class JSONLength(Func):
    function = 'jsonb_array_length'
    output_field = models.IntegerField()


class Category(models.Model):
    title = models.CharField(max_length=150, unique=True)
    slug = models.CharField(max_length=150, unique=True) # slug пока не надо, мб удалить в будущем


class CourseManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(moderated=True).annotate(
            students_count=JSONLength('students')).order_by('-price', '-students_count')


class Course(models.Model):
    author = models.PositiveIntegerField()
    author_name = models.CharField(max_length=250, blank=True)
    students = models.JSONField(default=list)
    category = models.ForeignKey(Category,
                                 related_name='courses',
                                 on_delete=models.PROTECT)

    title = models.CharField(max_length=200)
    slug = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    description = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    draft = models.BooleanField(default=True)
    moderated = models.BooleanField(default=False)

    published = CourseManager()
    objects = models.Manager()

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(unidecode(self.title))
        super(Course, self).save(*args, **kwargs)

    def is_student(self, user_id):
        return user_id in self.students
    

class Comment(models.Model):
    class Meta:
        abstract = True
    
    author = models.PositiveIntegerField()
    author_name = models.CharField(max_length=250, blank=True)
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)


class CourseComment(Comment):
    course = models.ForeignKey(Course,
                               on_delete=models.CASCADE,
                               related_name='comments')
    def __str__(self):
        return f'course comment by {self.author}: {self.body}'
    

class LessonManager(models.Manager):
    def get_published(self):
        return super().get_queryset().filter(moderated=True, draft=False)


class Lesson(models.Model):
    course = models.ForeignKey(Course,
                               on_delete=models.CASCADE,
                               related_name='lessons')
    
    title = models.CharField(max_length=200)
    slug = models.CharField(max_length=200) # мб убрать
    order = OrderField(blank=True, fields=['course'])
    draft = models.BooleanField(default=True)
    moderated = models.BooleanField(default=False)

    published = LessonManager()
    objects = models.Manager()

    def __str__(self):
        return f'{self.title} order {self.order}'
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super(Lesson, self).save(*args, **kwargs)
    
    class Meta:
        ordering = ['order']


class LessonComment(Comment):
    lesson = models.ForeignKey(Lesson,
                               on_delete=models.CASCADE,
                               related_name='comments')
    def __str__(self):
        return f'lesson comment by {self.author}: {self.body}'

    
class Content(models.Model):
    lesson = models.ForeignKey(Lesson,
                               on_delete=models.CASCADE,
                               related_name='contents')
    content_type = models.ForeignKey(ContentType,
                                     on_delete=models.CASCADE,
                                     limit_choices_to={'model__in':(
                                         'text',
                                         'url',
                                         'image',
                                         'file',
                                     )})
    obj_id = models.PositiveIntegerField()
    item = GenericForeignKey('content_type', 'obj_id')
    order = OrderField(blank=True, fields=['lesson'])

    class Meta:
        ordering = ['order']
        

class ItemBase(models.Model):
    class Meta:
        abstract = True

    def __str__(self):
        return f'{self.__class__.__name__}'
    

class Text(ItemBase):
    body = models.TextField()


class Image(ItemBase):
    image = models.ImageField(upload_to='images')


class File(ItemBase):
    file = models.FileField(upload_to='files')


class URL(ItemBase): # потом мб логичней будет поменять на URL
    url = models.URLField()