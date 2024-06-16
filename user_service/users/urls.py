from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('user-create/', views.UserCreateView.as_view(), name='user_create')
]
