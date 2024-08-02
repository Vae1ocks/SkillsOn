from django.db.models.signals import post_save, pre_delete
from django.db.models import Avg
from django.dispatch import receiver
from .models import CourseComment


@receiver(post_save, sender=CourseComment)
def update_course_rating_when_comment_save(sender, instance, **kwargs):
    course = instance.course
    comments = course.comments.all()
    if comments.exists():
        course.rating = comments.aggregate(Avg('rating'))['rating__avg']
    else:
        course.rating = 0
    course.save()


@receiver(pre_delete, sender=CourseComment)
def update_course_rating_when_comment_delete(sender, instance, **kwargs):
    course = instance.course
    comments = course.comments.exclude(id=instance.id)
    if comments.exists():
        course.rating = comments.aggregate(Avg('rating'))['rating__avg']
    else:
        course.rating = 0
    course.save()