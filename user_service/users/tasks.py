from celery import shared_task
from celery.signals import worker_ready
import pika
import json
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


@shared_task
def user_personal_info_updated_event(user_email, **kwargs):
    if 'first_name' in kwargs or 'last_name' in kwargs: # убрать localhost
        connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
        channel = connection.channel()
        channel.exchange_declare(exchange='user_update',
                                 exchange_type='direct')
        message = json.dumps({
            '''
            если пользователь не обновляет first/last_name, всё равно его получаем
            и обновляем вместе с ним.
            '''
            'user_email': user_email,
            'first_name': kwargs.get('first_name',
                                     get_user_model().objects.get(email=user_email).first_name),
            'last_name': kwargs.get('last_name', 
                                    get_user_model().objects.get(email=user_email).last_name)
        })

        channel.basic_publish(exchange='user_update',
                              routing_key='user.personal_info.update',
                              body=message)
        connection.close()

@shared_task
def user_email_updated_event(old_user_email, new_user_email):
    connection = pika.BlockingConnection(pika.ConnectionParametrs('rabbitmq'))
    channel = connection.channel()
    channel.exchange_declare(exchange='user_update',
                             exchange_type='direct')
    message = json.dumps({
        'old_user_email': old_user_email,
        'new_user_email': new_user_email
    })

    channel.basic_publish(exchange='user_update',
                          routing_key='user.email.update',
                          body=message)
    connection.close()

@shared_task
def user_password_updated_event(email, password):
    connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
    channel = connection.channel()
    channel.exchange_declare(exchange='user_update',
                             exchange_type='direct')
    message = json.dumps({
        'email': email,
        'password': password
    })

    channel.basic_publish(exchange='user_update',
                          routing_key='user.password.update',
                          body=message)
    connection.close()

@shared_task
def handle_user_password_reset_event():
    connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
    channel = connection.channel()
    channel.exchange_declare(exchange='auth_user_update',
                             exchange_type='direct')
    
    queue_result = channel.queue_declare(queue='password_reset_queue', exclusive=True)
    queue_name = queue_result.method.queue

    channel.queue_bind(queue=queue_name, routing_key='user.password.reset')

    def password_reset(ch, method, properties, body):
        data = json.loads(body)
        email = data['email']
        password = data['new_password']

        user = get_user_model().objects.get(email=email)
        user.set_password(password)
        user.save()

    channel.basic_consume(queue=queue_name, on_message_callback=password_reset,
                          auto_ack=True)
    channel.start_consuming()

@shared_task
def handle_user_created_event():
    connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
    channel = connection.channel()
    channel.exchange_declare(exchange='auth_user_update',
                             exchange_type='direct')
    queue_result = channel.queue_declare(queue='user_create_queue', exclusive=True)
    queue_name = queue_result.method.queue

    channel.queue_bind(queue=queue_name, routing_key='user.create')

    def user_create(ch, method, properties, body):
        data = json.loads(body)
        get_user_model().objects.create(**data)

@worker_ready.connect
def start(sender, **kwargs):
    with sender.app.connection() as conn:
        sender.app.send_task('handle_user_created_event')
        sender.app.send_task('handle_user_password_reset_event')