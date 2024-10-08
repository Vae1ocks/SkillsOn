from django.contrib import admin
from django.urls import path, include

from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework_simplejwt.views import TokenObtainPairView


urlpatterns = [
    path("users/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "users/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path("users/", include("users.urls", namespace="users")),
    path("users/payout/", include("payout.urls", namespace="payout")),
    path("users/login", TokenObtainPairView.as_view()),
    path("users/admin/", admin.site.urls),
]
