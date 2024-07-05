from celery import shared_task
from celery.signals import worker_ready
import json
import pika

from . import models

@shared_task
def handle_user_personal_info_updated_event():
    connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
    channel = connection.channel()
    channel.exchange_declare(exchange='user_update', exchange_type='direct')

    queue_result = channel.queue_declare(queue='personal_info_update_queue', exclusive=True)
    queue_name = queue_result.method.queue
    channel.queue_bind(exchange='user_update', queue=queue_name,
                       routing_key='user.personal_info.update')

    def personal_info_update(ch, method, properties, body):
        data = json.loads(body)
        email = data['user_email']
        first_name = data['first_name']
        last_name = data['last_name']

        models.Course.objects.filter(author=email).update(
            author_name=f'{first_name} {last_name[0]}.'
        )
        models.CourseComment.objects.filter(author=email).update(
            author_name=f'{first_name} {last_name[0]}.'
        )
        models.LessonComment.objects.filter(author=email).update(
            author_name=f'{first_name} {last_name[0]}.'
        )
    
    channel.basic_consume(queue=queue_name, on_message_callback=personal_info_update,
                          auto_ack=True)
    channel.start_consuming()

@shared_task
def handle_user_email_updated_event():
    connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
    channel = connection.channel()
    channel.exchange_declare(exchange='user_update', exchange_type='direct')
    
    queue_result = channel.queue_declare(queue='email_update_queue', exclusive=True)
    queue_name = queue_result.method.queue
    channel.queue_bind(exchange='user_update', queue=queue_name,
                       routing_key='user.email.update')
    
    def email_update(ch, method, properties, body):
        data = json.loads(body)
        old_email = data['old_user_email']
        new_email = data['new_user_email']

        models.Course.objects.filter(author=old_email).update(author=new_email)
        models.CourseComment.objects.filter(author=old_email).update(author=new_email)
        models.LessonComment.objects.filter(author=old_email).update(author=new_email)

    channel.basic_consume(queue=queue_name, on_message_callback=email_update,
                          auto_ack=True)
    channel.start_consuming()

@worker_ready.connect
def start(sender, **kwargs):
    with sender.app.connection() as conn:
        sender.app.send_task('handle_user_email_updated_event')
        sender.app.send_task('handle_user_personal_info_updated_event')