from celery import shared_task
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings


@shared_task
def send_confiramtion_code(email, body):
    send_mail(
        "Код подтверждения",
        body,
        settings.EMAIL_HOST_USER,
        [email],
        fail_silently=False,
    )


@shared_task(name="auth_service.update_user_email")
def update_user_email(old_user_email, new_user_email):
    user = get_user_model().objects.get(email=old_user_email)
    user.email = new_user_email
    user.save()


@shared_task(name="auth_service.update_user_password")
def update_user_password(email, password):
    user = get_user_model().objects.get(email=email)
    user.set_password(password)
    user.save()
