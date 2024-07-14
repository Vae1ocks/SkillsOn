from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('users/admin/', admin.site.urls),
    path('users/', include('users.urls', namespace='users')),
    path('users/payout/', include('payout.urls', namespace='payout'))
]