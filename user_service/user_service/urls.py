from django.contrib import admin
from django.urls import path, include

from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('users/api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('users/api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('users/admin/', admin.site.urls),
    path('users/', include('users.urls', namespace='users')),
    path('users/payout/', include('payout.urls', namespace='payout'))
]