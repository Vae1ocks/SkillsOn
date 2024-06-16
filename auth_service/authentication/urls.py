from django.urls import path
from . import views

app_name = 'authentication'

urlpatterns = [
    path('registration/user-data/', views.RegistrationView.as_view(),
         name='registration_user_data'),
    path('registration/confirmation/', views.RegistrationConfirmationView.as_view(),
         name='registration_email_confirmation'),
     path('registration/interests/', views.RegistrationCategoryChoiceView.as_view(),
          name='registration_category_choice'),
     path('login/', views.LoginView.as_view(), name='login')
]
