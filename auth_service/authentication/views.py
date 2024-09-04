from rest_framework.views import APIView
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response

from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.utils import timezone

from .serializers import *

from .tasks import send_confiramtion_code
from celery import current_app

from drf_spectacular.utils import extend_schema, inline_serializer

import requests
import random


class RegistrationView(APIView):
    serializer_class = UserSerializer # Только для drf_spectacular

    @extend_schema(
        description='Первый этап регистрации: ввод персональных данных.'
    )
    def post(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            confirmation_code = random.randint(100000, 999999)
            request.session['confirmation_code'] = confirmation_code
            request.session['registration_data'] = serializer.validated_data
            send_confiramtion_code.delay(
                email=serializer.validated_data['email'],
                body=f'Your confirmation code: {confirmation_code}'
            )
            return Response({'detail': 'ok'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

class RegistrationConfirmationView(APIView):
    serializer_class = ConfirmationCodeSerializer  # Только для drf_spectacular

    @extend_schema(
        description='Второй этап регистрации: ввод кода подтверждения, отправленного '
                    'на указанную электронную почту.'
    )
    def post(self, request, *args, **kwargs):
        serializer = ConfirmationCodeSerializer(data=request.data)
        if serializer.is_valid():
            if serializer.data['code'] == request.session.get('confirmation_code'):
                request.session['is_email_confirmed'] = True
                request.session.pop('confirmation_code')
                return Response({'detail': 'ok'}, status=status.HTTP_200_OK)
            return Response({'code': 'Неверный код подтверждения'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class RegistrationCategoryChoiceView(APIView):
    serializer_class = CategorySerializer # Только для drf_spectacular

    @extend_schema(
        description='Третий этап регистрации: выбор предпочтений. '
                    'Возвращает список json-объектов, что показаны в примере. '
                    '[{...}, {...}, {...}]',
    )
    def get(self, request, *args, **kwargs):
        if not request.session.get('is_email_confirmed'):
            return Response({'detail': 'Почта не подтверждена'}, status=status.HTTP_403_FORBIDDEN)
        base_uri = request.build_absolute_uri('/')
        relative_url = 'courses/category-list/'
        url = f'{base_uri}{relative_url}'
        response = requests.get(url)
        if response.status_code == 200:
            categories = response.json()
            return Response(categories, status=status.HTTP_200_OK)
        return Response({'detail': 'Невозможно получить категории'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        description='Третий этапе регистрации: выбор предпочитаемых категорий. '
                    '(Категории получить можно через get-запрос на этот ендпоинт).',
        request=CategorySerializer(many=True)
    )
    def post(self, request, *args, **kwargs):
        if not request.session.get('is_email_confirmed'):
            return Response({'detail': 'Почта не подтверждена'}, status=status.HTTP_403_FORBIDDEN)
        serializer = CategorySerializer(data=request.data, many=True)
        if len(serializer.validated_data) < 3:
            raise serializers.ValidationError(
                'Вы должны выбрать минимум 3 предпочтения'
            )
        if serializer.is_valid():
            registration_data = request.session.pop('registration_data', None)
            if not registration_data:
                return Response(
                    {'detail':'Данные для регистрации'
                              'не предоставлены'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            categories_liked = serializer.data
            full_reg_data = {**registration_data, 'categories_liked': []}
            for category in categories_liked:
                full_reg_data['categories_liked'].append(category)
            user_serializer = UserSerializer(data=registration_data)
            if user_serializer.is_valid():
                current_app.send_task(
                    'user_service.create_user',
                    kwargs={**full_reg_data},
                    queue='user_service_queue'
                )
                user_serializer.save()
                return Response(
                    user_serializer.data, status=status.HTTP_201_CREATED
                )
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )
        return Response(
            serializer.errors, status=status.HTTP_400_BAD_REQUEST
        )


class PasswordResetView(APIView):
    serializer_class = EmailSerializer # Только для drf_spectacular

    @extend_schema(description='Первый этап сброса пароля: ввод почты')
    def post(self, request, *args, **kwargs):
        serializer = EmailSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = get_user_model().objects.filter(email=email)
            if user:
                confirmation_code = random.randint(100000, 999999)
                request.session['confirmation_code'] = confirmation_code
                request.session['email'] = email
                send_mail(
                    'Confirm your email',
                    f'Your confirmation code: {confirmation_code}',
                    settings.EMAIL_HOST_USER,
                    [email]
                )
                return Response(
                    {'detail': 'ok'}, status=status.HTTP_200_OK
                )
            return Response(
                {'detail': 'Неверный email'},
                status=status.HTTP_404_NOT_FOUND
            )
        return Response(
            serializer.errors, status=status.HTTP_400_BAD_REQUEST
        )
    

class PasswordResetConfirmationView(APIView):
    serializer_class = ConfirmationCodeSerializer # Только для drf_spectacular

    @extend_schema(description='Второй этап сброса пароля: '
                               'ввод кода, отправленного на почту')
    def post(self, request, *args, **kwargs):
        serializer = ConfirmationCodeSerializer(data=request.data)
        if serializer.is_valid():
            if serializer.data['code'] == request.session.get(
                'confirmation_code'
            ):
                request.session['is_email_confirmed'] = True
                request.session.pop('confirmation_code')
                return Response(
                    {'detail': 'ok'}, status=status.HTTP_200_OK
                )
            return Response(
                {'code': 'Неверный код подтверждения'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(
            serializer.errors, status=status.HTTP_400_BAD_REQUEST
        )
    

class PasswordResetNewPasswordView(APIView):
    serializer_class = PasswordSerializer # Только для drf_spectacular

    @extend_schema(description='Третий этап сброса пароля: ввод нового пароля. '
                               '(Повторный ввод нового пароля для подтверждения '
                               'по задумке запрашивается лишь во фронтенде).')
    def post(self, request, *args, **kwargs):
        if not request.session.get('is_email_confirmed'):
            return Response(
                {'detail': 'Email not confirmed'},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer = PasswordSerializer(data=request.data)
        if serializer.is_valid():
            password = serializer.validated_data['password']
            email = request.session.get('email')
            user_exists = get_user_model().\
                objects.filter(email=email).exists()
            if user_exists:
                user = get_user_model().objects.get(email=email)
                current_app.send_task(
                    'user_service.update_reset_password',
                    kwargs={
                        'email': email,
                        'new_password': password
                    }, queue='user_service_queue'
                )
                user.set_password(password)
                user.save()
                request.session.pop('is_email_confirmed', None)
                request.session.pop('email', None)
                return Response(
                    {'detail': 'Пароль успешно обновлён'},
                    status=status.HTTP_200_OK
                )
            return Response(
                {'detail': 'Неверный email, пользователь не найден'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(
            serializer.errors, status=status.HTTP_400_BAD_REQUEST
        )
