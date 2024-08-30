from django.contrib import admin
from django.urls import path, include

from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('auth/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('auth/docs/', SpectacularSwaggerView.as_view(url_name='schema'),
         name='swagger-ui'),
    path('auth/admin/', admin.site.urls),
    path('auth/', include('authentication.urls', namespace='authentication')),
]
