from celery import shared_task
from django.contrib.auth import get_user_model


@shared_task(name='auth_service.update_user_email')
def update_user_email(old_user_email, new_user_email):
    user = get_user_model().objects.get(email=old_user_email)
    user.email = new_user_email
    user.save()

@shared_task(name='auth_service.update_user_password')
def update_user_password(email, password):
    user = get_user_model().objects.get(email=email)
    user.set_password(password)
    user.save()