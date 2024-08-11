from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings
from celery import current_app
import stripe.error
from payment.models import Order
from courses.models import Course
from drf_spectacular.utils import extend_schema
import stripe


def payment_succeeded(order):
    order.completed = True
    order.save()
    user_email = order.user
    course_id = order.course.id
    course = Course.objects.get(id=course_id)
    course.students.add(user_email)
    course.save()

    user_profit = order.price * 0.8
    current_app.send_task(
        'user_service.profit_income',
        kwargs={
            'user_id': course.author,
            'profit': user_profit
        }, queue='user_service_queue'
    )


@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhook(APIView):
    def post(self, request, *args, **kwargs):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        event = None
        try:
            event = stripe.Webhook.construct_event(
                payload,
                sig_header,
                settings.STRIPE_WEBHOOK_SECRET
            )
        except ValueError as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        except stripe.error.SignatureVerificationError as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            if session['mode'] == 'payment' and session['payment_status'] == 'paid':
                try:
                    order = Order.objects.get(id=session['client_reference_id'])
                except Order.DoesNotExist:
                    return Response(status.HTTP_404_NOT_FOUND)
                payment_succeeded(order)
        return Response(status=status.HTTP_200_OK)
    

@method_decorator(csrf_exempt, name='dispatch')
class YooKassaPaymentWebhook(APIView):
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    @extend_schema(
            description='Во фронте не нужно, сюда Yookassa отправит уведомление об оплате '
                        'Т.е этот ендпоинт для взаимодействия бэка с юкассой'
    )
    def post(self, request, *args, **kwargs):
        # ip, с которых YooKassa шлёт уведомления
        allowed_ips = [
            '185.71.76.0/27',
            '185.71.77.0/27',
            '77.75.153.0/25',
            '77.75.156.11',
            '77.75.156.35',
            '77.75.154.128/25',
            '2a02:5180::/32'
        ]

        ip = self.get_client_ip(request)
        if ip not in allowed_ips:
            return Response(status=status.HTTP_403_FORBIDDEN)
        payload = request.data
        if payload['event'].split('.')[0] == 'payment':
            if payload['status'] == 'succeeded':
                try:
                    order = Order.objects.get(payload['metadata']['order_id'])
                except Order.DoesNotExist:
                    return Response(status=status.HTTP_404_NOT_FOUND)
                payment_succeeded(order)
        return Response(status=status.HTTP_200_OK)