from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('courses/admin/', admin.site.urls),
    path('courses/', include('courses.urls', namespace='courses')),
    path('courses/payment/', include('payment.urls', namespace='payment'))
]
