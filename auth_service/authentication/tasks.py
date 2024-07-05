from celery import shared_task
from celery.signals import worker_ready
import pika
import json
from django.contrib.auth import get_user_model

@shared_task
def handle_user_email_updated_event():
    connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
    channel = connection.channel()
    channel.exchange_declare(exchange='user_update', exchange_type='direct')

    queue_result = channel.queue_declare(queue='auth_email_update_queue', exclusive=True)
    queue_name = queue_result.method.queue

    channel.queue_bind(exchange='user_update', queue=queue_name,
                       routing_key='user.email.update')
    
    def email_update(ch, method, properties, body):
        data = json.loads(body)
        old_email = data['old_user_email']
        new_email = data['new_user_email']

        user = get_user_model().objects.get(email=old_email)
        user.email = new_email
        user.save()

    channel.basic_consume(queue=queue_name, on_message_callback=email_update,
                          auto_ack=True)
    channel.start_consuming()
    
@shared_task
def handle_user_password_updated_event():
    connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
    channel = connection.channel()
    channel.exchange_declare(exchange='user_update', exchange_type='direct')

    queue_result = channel.queue_declare(queue='auth_password_update_queue', exclusive=True)
    queue_name = queue_result.method.queue

    channel.queue_bind(exchange='user_update', queue=queue_name,
                       routing_key='user.password.update')
    
    def password_update(ch, method, properties, body):
        data = json.loads(body)
        email = data['email']
        password = data['password']

        user = get_user_model().objects.get(email=email)
        user.set_password(password)
        user.save()

    channel.basic_consume(queue=queue_name, on_message_callback=password_update,
                          auto_ack=True)
    channel.start_consuming()
    
@shared_task
def user_password_reset_event(email, new_password):
    connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
    channel = connection.channel()
    channel.exchange_declare(exchange='auth_user_update',
                             exchange_type='direct')
    message = json.dumps({
        'email': email,
        'new_password': new_password
    })

    channel.basic_publish(exchange='auth_user_update',
                          routing_key='user.password.reset',
                          body=message)
    connection.close()

@shared_task
def user_created_event(**kwargs):
    connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
    channel = connection.channel()
    channel.exchange_declare(exchange='auth_user_update',
                             exchange_type='direct')
    message = json.dumps(kwargs)

    channel.basic_publish(exchange='auth_user_update',
                          routing_key='user.create',
                          body=message)
    connection.close()

@worker_ready.connect
def start(sender, **kwargs):
    with sender.app.connection() as conn:
        sender.app.send_task('handle_user_email_updated_event')
        sender.app.send_task('handle_user_password_updated_event')