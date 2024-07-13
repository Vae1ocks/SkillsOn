from rest_framework.views import APIView
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from .serializers import UserSerializer, ConfirmationCodeSerializer,\
    CategorySerializer, EmailSerializer, PasswordSerializer, EmailTokenObtainPairSerializer
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from rest_framework_simplejwt.views import TokenObtainPairView
from .tasks import user_password_reset_event, user_created_event
import datetime
import requests
import random
import jwt


class RegistrationView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            confirmation_code = random.randint(100000, 999999)
            request.session['confirmation_code'] = confirmation_code
            request.session['registration_data'] = serializer.validated_data
            send_mail(
                'Confirmate your email',
                f'Your confirmation code: {confirmation_code}', # Тут нужна асинхронность
                settings.EMAIL_HOST_USER,
                [serializer.validated_data['email']]
            )
            return Response({'detail': 'ok'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

class RegistrationConfirmationView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = ConfirmationCodeSerializer(data=request.data)
        if serializer.is_valid():
            if serializer.data['code'] == request.session.get('confirmation_code'):
                request.session['is_email_confirmed'] = True
                request.session.pop('confirmation_code')
                return Response({'detail': 'ok'}, status=status.HTTP_200_OK)
            return Response({'code': 'Confirmation code is incorrect'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class RegistrationCategoryChoiceView(APIView):
    def get(self, request, *args, **kwargs):
        if not request.session.get('is_email_confirmed'):
            return Response({'detail': 'Email not confirmed'}, status=status.HTTP_403_FORBIDDEN)
        url = 'http://127.0.0.1:8002/category-list/'
        response = requests.get(url)
        if response.status_code == 200:
            categories = response.json()
            return Response(categories, status=status.HTTP_200_OK)
        return Response({'detail': 'Unable to fetch categories'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request, *args, **kwargs):
        if not request.session.get('is_email_confirmed'):
            return Response({'detail': 'Email not confirmed'}, status=status.HTTP_403_FORBIDDEN)
        serializer = CategorySerializer(data=request.data, many=True)
        if serializer.is_valid():
            registration_data = request.session.pop('registration_data', None)
            if not registration_data:
                return Response({'detail': 'Registration data not found in session'}, status=status.HTTP_400_BAD_REQUEST)
            categories_liked = serializer.data
            full_reg_data = {**registration_data, 'categories_liked': []}
            for category in categories_liked:
                full_reg_data['categories_liked'].append(category)
            user_serializer = UserSerializer(data=registration_data)
            if user_serializer.is_valid():
                user_created_event.delay(**full_reg_data)
                user_serializer.save()
                return Response(user_serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')
        if not email or not password:
            return Response({'detail': 'Email and password are required'}, status=status.HTTP_400_BAD_REQUEST)
        user = authenticate(request,
                            email=email,
                            password=password)
        if user is not None:
            if user.is_active:
                data = {
                    'id': user.id,
                    'exp': timezone.now() + datetime.timedelta('days=10'),
                    'iat': timezone.now()
                }
                token = jwt.encode(data, settings.SECRET_KEY, algorithm='HS256')
                return Response({'token': token}, status=status.HTTP_200_OK)
            return Response({'detail': 'Account is banned'}, status=status.HTTP_403_FORBIDDEN)
        return Response({'detail': 'Invalid data'}, status=status.HTTP_404_NOT_FOUND)
    

class PasswordResetView(APIView):
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
                return Response({'detail': 'ok'}, status=status.HTTP_200_OK)
            return Response({'detail': 'Invalid email, user not found'},
                            status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class PasswordResetConfirmationView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = ConfirmationCodeSerializer(data=request.data)
        if serializer.is_valid():
            if serializer.data['code'] == request.session.get('confirmation_code'):
                request.session['is_email_confirmed'] = True
                request.session.pop('confirmation_code')
                return Response({'detail': 'ok'}, status=status.HTTP_200_OK)
            return Response({'code': 'Confirmation code is incorrect'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class PasswordResetNewPasswordView(APIView):
    def post(self, request, *args, **kwargs):
        if not request.session.get('is_email_confirmed'):
            return Response({'detail': 'Email not confirmed'}, status=status.HTTP_403_FORBIDDEN)
        serializer = PasswordSerializer(data=request.data)
        if serializer.is_valid():
            password = serializer.validated_data['password']
            email = request.session.get('email')
            user_exists = get_user_model().objects.filter(email=email).exists()
            if user_exists:
                user = get_user_model().objects.get(email=email)
                user_password_reset_event.delay(email=email, new_password=password)
                user.set_password(password)
                user.save()
                request.session.pop('is_email_confirmed', None)
                request.session.pop('email', None)
                return Response({'detail': 'Password updated successfully'}, status=status.HTTP_200_OK)
            return Response({'detail': 'invalid email, user not found'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
from rest_framework_simplejwt.authentication import JWTTokenUserAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response


class ExampleView(APIView):
    authentication_classes = [JWTTokenUserAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        print('Ща чёт будет')
        request.user.email = 'user@user.com'
        print(request.user)
        return Response({"message": f"Hello, {request.user.email}! \
                         Your name is {request.user.first_name} + {request.user.last_name}"})

class EmailTokenObtainPairView(TokenObtainPairView):
    serializer_class = EmailTokenObtainPairSerializer