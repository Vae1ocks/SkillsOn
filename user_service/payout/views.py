from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import UserPayout
from .tasks import check_payout_status
from yookassa import Payout
import uuid


class YooKassaPayoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        payout_token = request.data.get('payout_token')
        value = request.data.get('value')
        user = get_user_model().objects.get(email=request.user.email)
        if user.balance < value:
            raise ValidationError('Недостаточно средств')
        if not payout_token or not value:
            raise ValidationError('Не переданы данные для платежа')
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