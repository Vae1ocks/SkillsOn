from celery import shared_task
from . import models


@shared_task(name='courses_service.update_personal_info')
def update_personal_info(user_id, first_name, last_name):
    models.Course.objects.filter(author=user_id).update(
        author_name=f'{first_name} {last_name[0]}.'
    )
    models.CourseComment.objects.filter(author=user_id).update(
        author_name=f'{first_name} {last_name[0]}.'
    )
    models.LessonComment.objects.filter(author=user_id).update(
        author_name=f'{first_name} {last_name[0]}.'
    )