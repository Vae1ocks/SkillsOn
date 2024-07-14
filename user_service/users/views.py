from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView, RetrieveDestroyAPIView,\
    UpdateAPIView, ListAPIView, RetrieveAPIView
from rest_framework import status
from .permissions import IsRequestUserProfile
from .models import Chat
from . import serializers
from django.contrib.auth import get_user_model
from . import tasks
import random


class UserPersonalInfoUpdateView(APIView):
    permission_classes = [IsAuthenticated, IsRequestUserProfile]

    def post(self, request, *args, **kwargs):
        serializer = serializers.UserPersonalInfoSerializer(data=request.data)
        if serializer.is_valid():
            validated_data = serializer.validated_data
            id = request.user.id
            if 'first_name' in validated_data or 'last_name' in validated_data:
                tasks.user_personal_info_updated_event.delay(
                    user_id=id,
                    first_name=validated_data.get('first_name'),
                    last_name=validated_data.get('last_name')
                )
            user = get_user_model().objects.get(id=id)
            for attr, val in validated_data.items():
                setattr(user, attr, val)
            user.save()
            return Response({'detail': 'ok'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ConfirmationOldEmailView(APIView):
    permission_classes = [IsAuthenticated, IsRequestUserProfile]

    def get(self, request, *args, **kwargs):
        confirmation_code = random.randint(100000, 999999)
        request.session['confirmation_code'] = confirmation_code
        user = get_user_model().objects.get(id=request.user.id)
        body = f'Ваш код для подтверждения текущей почты: {confirmation_code}'
        tasks.send_confirmation_code.delay(body=body, email=user.email)
        return Response({'detail': 'Код был выслан'}, status=status.HTTP_200_OK)
    
    def post(self, request, *args, **kwargs):
        serializer = serializers.ConfirmationCodeSerializer(data=request.data)
        if serializer.is_valid():
            entered_code = serializer.validated_data['code']
            exp_code = request.session.get('confirmation_code', '')
            if exp_code:
                if exp_code == entered_code:
                    request.session['email_confirmated'] = True
                    request.session.pop('confirmation_code')
                    return Response({'detail': 'ok'}, status=status.HTTP_200_OK)
                return Response({'detail': 'Неверный код'},
                                status=status.HTTP_400_BAD_REQUEST)
            return Response({'detail': 'Требуется ввод кода'},
                            status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmailUpdateSetNewEmailView(APIView):
    permission_classes = [IsAuthenticated, IsRequestUserProfile]

    def post(self, request, *args, **kwargs):
        if request.session.get('email_confirmated'):
            serializer = serializers.EmailSerializer(data=request.data)
            if serializer.is_valid():
                email = serializer.validated_data['email']
                if not get_user_model().objects.filter(email=email).exists():
                    confirmation_code = random.randint(100000, 999999)
                    request.session['confirmation_code'] = confirmation_code
                    body = f'Код подтверждения для смены почты: {confirmation_code}'
                    tasks.send_confirmation_code.delay(body=body, email=email)
                    request.session.pop('email_confirmated')
                    return Response({'detail': 'Код подтверждения выслан'},
                                    status=status.HTTP_200_OK)
                return Response({'detail': 'Пользователь с данной почтой уже существует'},
                                status=status.HTTP_409_CONFLICT)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_403_FORBIDDEN)
    

class EmailUpdateFinish(APIView):
    permission_classes = [IsAuthenticated, IsRequestUserProfile]

    def post(self, request, *args, **kwargs):
        serializer = serializers.EmailWithConfirmationCodeSerializer(
            data=request.data
        )
        if serializer.is_valid():
            exp_code = request.session.get('confirmation_code')
            if exp_code:
                entered_code = serializer.validated_data['code']
                if exp_code == entered_code:
                    email = serializer.validated_data['email']
                    user = get_user_model().objects.get(id=request.user.id)
                    tasks.user_email_updated_event.delay(old_user_email=user.email,
                                                   new_user_email=email)
                    user.email = email
                    user.save()
                    return Response({'detail': 'ok'}, status=status.HTTP_200_OK)
                return Response({'detail': 'Неверный код'},
                                status=status.HTTP_400_BAD_REQUEST)
            return Response({'detail': 'Требуется ввод кода'},
                            status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class PasswordChangeView(APIView):
    permission_classes = [IsAuthenticated, IsRequestUserProfile]

    def post(self, request, *args, **kwargs):
        serializer = serializers.ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            tasks.user_password_updated_event.delay(
                email=get_user_model().objects.get(id=request.user.id).email,
                password=serializer.validated_data['new_password']
            )
            serializer.save()
            return Response({'detail': 'Пароль успешно обновлён'},
                            status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChatListView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.ChatSerializer

    def get_queryset(self):
        user = get_user_model().objects.get(id=self.request.user.id)
        return Chat.objects.filter(users__id=user.id)
    

class ChatRetrieveView(RetrieveDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.ChatDetailSerializer

    def get_queryset(self):
        user = get_user_model().objects.get(id=self.request.user.id)
        return Chat.objects.filter(users__id=user.id)
    

class UserListView(ListAPIView):
    serializer_class = serializers.UserListSerializer
    queryset = get_user_model().objects.all()


class UserDetailView(RetrieveAPIView):
    queryset = get_user_model().objects.all()
    
    def get_serializer_class(self):
        if self.request.user.id == self.get_object().id:
            return serializers.UserSerializer
        return serializers.OtherUserSerializer