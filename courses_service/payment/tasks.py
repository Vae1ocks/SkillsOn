from celery import shared_task
from celery.signals import worker_ready
import json
import pika

from . import models


@shared_task
def user_profit_income_event(author, profit):
    connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
    channel = connection.channel()
    channel.exchange_declare(exchange='user_update',
                             exchange_type='direct')
    message = json.dumps(
        {
            'author': author,
            'profit': profit
        }
    )

    channel.basic_publish(exchange='user_update',
                          routing_key='user.profit.income',
                          body=message)
    connection.close()