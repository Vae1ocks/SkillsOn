from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import UserPayout
from yookassa import Payout, Configuration
from django.conf import settings
from drf_spectacular.utils import extend_schema, inline_serializer, OpenApiExample
from .serializers import serializers
import uuid

Configuration.account_id = settings.YOOKASSA_ACCOUNT_ID
Configuration.secret_key = settings.YOOKASSA_SECRET_KEY

class YooKassaPayoutView(APIView):
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
            description='Для осуществления выплат. Требуется токен, полученный '
                        'от формы ЮКассы ввода данных карты.',
            request=inline_serializer(
                name='YooKassaPayoutSerializer',
                fields={
                    'payout_token': serializers.CharField(),
                    'value': serializers.IntegerField()
                }
            ),
            responses={
                202: inline_serializer(
                    name='PayoutCreated',
                    fields={'detail': serializers.CharField}
                )
            }
    )  
    def post(self, request, *args, **kwargs):
        payout_token = request.data.get('payout_token')
        value = request.data.get('value')
        user = get_user_model().objects.get(id=request.user.id)
        if user.balance < value:
            return Response({'detail': 'Недостаточно средств'},
                            status=status.HTTP_400_BAD_REQUEST)
        if not payout_token or not value:
            return Response({'detail': 'Не переданы данные для платежа'},
                            status=status.HTTP_400_BAD_REQUEST)
        idempotence_key = str(uuid.uuid4())

        user_payout = UserPayout.objects.create(
            user=user,
            value=value,
            status='pending'
        )

        payout = Payout.create(
            {
                'amount': {
                    'value': value,
                    'currency': 'RUB'
                },
                'payout_token': payout_token,
                'description': 'Вывод средств',
                'metadata': {
                    'user_email': user.email,
                    'user_payout_id': user_payout.id
                }

            }, idempotence_key
        )

        return Response({'detail': 'Выплата успешно создана'}, status=status.HTTP_202_ACCEPTED)