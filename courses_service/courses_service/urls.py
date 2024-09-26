from django.contrib import admin
from django.urls import path, include

from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path("courses/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "courses/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path("courses/admin/", admin.site.urls),
    path("courses/", include("courses.urls", namespace="courses")),
    path("courses/payment/", include("payment.urls", namespace="payment")),
]
