from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model


@shared_task
def send_confirmation_code(body, email):
    send_mail(
        'Код подтверждения',
        body,
        settings.EMAIL_HOST_USER,
        [email],
        fail_silently=False
    )

@shared_task(name='user_service.update_reset_password')
def update_reset_password(email, password):
    user = get_user_model().objects.get(email=email)
    user.set_password(password)
    user.save()

@shared_task(name='user_service.create_user')
def create_user(**data):
    # preference_data = data.pop('')
    get_user_model().objects.create_user(**data)

@shared_task(name='user_service.profit_income')
def profit_income(user_id, profit):
    user = get_user_model().objects.get(id=user_id)
    user.balance += profit
    user.save()