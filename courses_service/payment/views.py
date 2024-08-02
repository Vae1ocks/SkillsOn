from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .serializers import OrderSerializer
from django.contrib.auth import get_user_model
from yookassa import Configuration, Payment, Payout
from django.conf import settings
from django.urls import reverse, reverse_lazy
import stripe
import uuid

Configuration.account_id = settings.YOOKASSA_ACCOUNT_ID
Configuration.secret_key = settings.YOOKASSA_SECRET_KEY

class YookassaPaymentView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            order = serializer.save(completed=False)
            idempotence_key = uuid.uuid64()
            payment = Payment.create(
                {
                    'amount': {
                        'value': str(order.price),
                        'currency': 'RUB'
                    },
                    'confirmation': {
                        'type': 'redirect',
                        'return_url': reverse_lazy('courses:course-list')
                    },
                    'capture': True,
                    'description': order.__str__(),
                    'metadata': {'order_id': order.id},
                    'test': True
                }, idempotency_key=idempotence_key
            )
            return Response(
                {'confirmation_url': payment.confirmation['confirmation_url']},
                status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)      

class StripePayment(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        success_url = request.data.pop('success_url', '')
        cancel_url = request.data.pop('cancel_url', '')
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            order = serializer.save(completed=False)
            success_url = request.build_absolute_uri(reverse('payment:success'))
            cancel_url = request.build_absolute_uri(reverse('payment:canceled'))

            session_data = {
                'mode': 'payment',
                'client_reference_id': order.id,
                'success_url': success_url,
                'cancel_url': cancel_url,
                'line_items': [
                    {
                        'price_data': {
                            'unit_amount': int(order.price),
                            'currency': 'rub',
                            'product_data': {
                                'name': order.course.title
                            },
                        }, 'quantity': 1,
                    },
                ]
            }

            session = stripe.checkout.Session.create(**session_data)
            return Response({'stripe_url': session.url}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)