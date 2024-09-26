from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth import get_user_model

from .models import UserPayout

from drf_spectacular.utils import extend_schema


@method_decorator(csrf_exempt, name="dispatch")
class YookassaPayoutWebhook(APIView):
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip

    @extend_schema(description="Ендпонит только для ЮКассы, не дл фронта")
    def post(self, request, *args, **kwargs):
        allowed_ips = [
            "185.71.76.0/27",
            "185.71.77.0/27",
            "77.75.153.0/25",
            "77.75.156.11",
            "77.75.156.35",
            "77.75.154.128/25",
            "2a02:5180::/32",
        ]
        ip = self.get_client_ip(request)
        if ip not in allowed_ips:
            return Response(status=status.HTTP_403_FORBIDDEN)

        payload = request.data
        user_payout = UserPayout.objects.get(id=payload["metadata"]["user_payout_id"])
        value = payload["object"]["amount"]["value"]
        if payload["event"].split(".")[0] == "payout":
            if payload["status"] == "succeeded":
                user = get_user_model().objects.get(
                    email=payload["metadata"]["user_email"]
                )
                user.balance -= value
                user.save()
                user_payout.status = "succeeded"
                user_payout.save()
            elif payload["status"] == "canceled":
                user_payout.status = "canceled"
                user_payout.save()

        return Response(status=status.HTTP_200_OK)
