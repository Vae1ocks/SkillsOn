from django.urls import path
from . import views
from . import webhooks

app_name = "payout"

urlpatterns = [
    path(
        "yookassa/create/", views.YooKassaPayoutView.as_view(), name="yookassa_payout"
    ),
    path(
        "yookassa/webhook/",
        webhooks.YookassaPayoutWebhook.as_view(),
        name="yookassa_payout_webhook",
    ),
]
