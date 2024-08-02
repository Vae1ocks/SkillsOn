from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenRefreshView


app_name = 'authentication'

urlpatterns = [
     path('registration/user-data/', views.RegistrationView.as_view(),
         name='registration_user_data'),
     path('registration/confirmation/', views.RegistrationConfirmationView.as_view(),
         name='registration_email_confirmation'),
     path('registration/interests/', views.RegistrationCategoryChoiceView.as_view(),
          name='registration_category_choice'),
     path('password-reset/', views.PasswordResetView.as_view(), name='password_reset'),
     path('password-reset/email-confirmation/', views.PasswordResetConfirmationView.as_view(),
          name='password_reset_confirmation'),
     path('password-reset/new-password/', views.PasswordResetNewPasswordView.as_view(),
          name='password_reset_new_password'),
     # path('login/', views.LoginView.as_view(), name='login'),
     path('api/token/', views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
     path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]