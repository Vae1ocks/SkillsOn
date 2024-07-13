from django.urls import path
from . import views
from . import webhooks

app_name = 'payment'

urlpatterns = [
    # path('stripe/process/', views.StripePayment.as_view(), name='stripe_process'),
    # path('stripe/process/', views.StripePayment.as_view(), name='stripe_process'),
    path('yookassa/process/', views.YookassaPaymentView.as_view(), name='yookassa_process'),
    path('yookassa/webhook/', webhooks.YooKassaPaymentWebhook.as_view(), name='yookassa_process')
]