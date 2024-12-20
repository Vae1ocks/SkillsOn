from django.db import models
from django.db.models import Func, F
from django.db.models import Count
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify

from .fields import OrderField

from unidecode import unidecode


class JSONLength(Func):
    """
    Для подсчёта длины поля json.
    """

    function = "jsonb_array_length"
    output_field = models.IntegerField()


def category_image_upload_to(instance, filename):
    return f"categories/{instance.title}"


class Category(models.Model):
    """
    Категории курсов.
    """

    title = models.CharField(max_length=150, unique=True)
    slug = models.CharField(max_length=150, unique=True)
    image = models.ImageField(
        upload_to=category_image_upload_to,
        blank=True,
        null=True,
    )

    def __str__(self):
        return f"Category {self.title}"


class CourseManager(models.Manager):
    """
    Для сортировки курсов по количеству студентов и цене.
    """

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(moderated=True)
            .annotate(students_count=JSONLength("students"))
            .order_by("-price", "-students_count")
        )


class Course(models.Model):
    """
    Модель курсов.
    """

    author = models.PositiveIntegerField()
    author_name = models.CharField(max_length=250, blank=True)
    author_image = models.ImageField(
        upload_to="courses/%Y/%m/%d/", blank=True, null=True
    )

    students = models.JSONField(default=list, blank=True)

    category = models.ForeignKey(
        Category, related_name="courses", on_delete=models.PROTECT
    )

    title = models.CharField(max_length=200)
    slug = models.CharField(max_length=200, blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    description = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)

    LEVEL_CHOICES = (
        ("high", "Высокий"),
        ("medium", "Средний"),
        ("low", "Начальный"),
    )
    level = models.CharField(max_length=15, choices=LEVEL_CHOICES, default="low")

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
    """
    Абстрактная модель комментария.
    """

    class Meta:
        abstract = True

    author = models.PositiveIntegerField()
    author_name = models.CharField(max_length=250, blank=True)
    author_image = models.ImageField(
        upload_to="comments/%Y/%m/%d/", blank=True, null=True
    )

    body = models.TextField()

    created = models.DateTimeField(auto_now_add=True)


class CourseComment(Comment):
    """
    Модель комментария к курсу.
    """

    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="comments"
    )

    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )

    def __str__(self):
        return f"course comment by {self.author}: {self.body}"


class LessonManager(models.Manager):
    """
    Для фильтрации курсов по тому, помечены ли они к публикации и
    прошли ли модерацию.
    """

    def get_published(self):
        return super().get_queryset().filter(moderated=True, draft=False)


class Lesson(models.Model):
    """
    Модель урока курса.
    """

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="lessons")

    title = models.CharField(max_length=200)
    slug = models.CharField(max_length=200)
    order = OrderField(blank=True, fields=["course"])
    draft = models.BooleanField(default=True)
    moderated = models.BooleanField(default=False)
    users_seen = models.JSONField(default=list, blank=True)

    published = LessonManager()
    objects = models.Manager()

    def __str__(self):
        return f"{self.title} order {self.order}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super(Lesson, self).save(*args, **kwargs)

    class Meta:
        ordering = ["order"]


class LessonComment(Comment):
    """
    Модель комментария к уроку курса.
    Урок является связующим объектов Content.
    """

    lesson = models.ForeignKey(
        Lesson, on_delete=models.CASCADE, related_name="comments"
    )
    reply_to = models.ForeignKey(
        "self", on_delete=models.CASCADE, related_name="replies", null=True, blank=True
    )
    quote_text = models.CharField(max_length=210, null=True, blank=True)
    is_note = models.BooleanField(
        default=False
    )  # возможно оставлять как комментарии, так и заметки для себя

    def __str__(self):
        return f"lesson comment by {self.author}: {self.body}"


class Content(models.Model):
    """
    Модель контента к уроку.
    """

    lesson = models.ForeignKey(
        Lesson, on_delete=models.CASCADE, related_name="contents"
    )
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        limit_choices_to={
            "model__in": (
                "text",
                "url",
                "image",
                "file",
            )
        },
    )
    obj_id = models.PositiveIntegerField()
    item = GenericForeignKey("content_type", "obj_id")
    order = OrderField(blank=True, fields=["lesson"])

    class Meta:
        ordering = ["order"]


class ItemBase(models.Model):
    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.__class__.__name__}"


class Text(ItemBase):
    body = models.TextField()


class Image(ItemBase):
    image = models.ImageField(upload_to="images")


class File(ItemBase):
    file = models.FileField(upload_to="files")


class URL(ItemBase):  # потом мб логичней будет поменять на URL
    url = models.URLField()
