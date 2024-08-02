from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('update/pesonal-info/', views.UserPersonalInfoUpdateView.as_view(),
         name='personal_info_update'),
    path('update/email/confirmation/old-email/', views.ConfirmationOldEmailView.as_view(),
         name='email_update_confirmation_old_email'),
    path('update/email/set-new-email/', views.EmailUpdateSetNewEmailView.as_view(),
         name='email_update_set_new_email'),
    path('update/email/confirmation/new-email', views.EmailUpdateFinish.as_view(),
         name='email_update_confirmation_new_email'),
    path('update/password/', views.PasswordChangeView.as_view(), name='password_update'),
    path('chat/', views.ChatListView.as_view(), name='chat_list'),
    path('chat/<int:pk>/', views.ChatRetrieveView.as_view(), name='chat_retrieve'),
    path('user-list/', views.UserListView.as_view(), name='user_list'),
    path('user/<int:pk>/', views.UserDetailView.as_view(), name='user_detail'),
    path('user/<int:id>/personal-preferences/',
          views.UserPreferencesView.as_view(), name='user_preferences'),
    path('user/<int:id>/personal-info/', views.UserPersonalInfoView.as_view(), name='user_info') 
]