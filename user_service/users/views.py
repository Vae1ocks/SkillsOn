from django.http import Http404, HttpResponseRedirect
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from .serializers import UserSerializer
from django.contrib.auth import get_user_model


class UserCreateView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class UserPasswordResetView(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        email = data.get('email')
        password = data.get('new_password')
        user_exists = get_user_model().objects.filter(email=email).exists()
        if user_exists:
            user = get_user_model().objects.get(email=email)
            if password is not None:
                user.set_password(password)
                user.save()
                return Response({'detail': 'ok'}, status=status.HTTP_200_OK)
            return Response({'detail': 'password not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'detail': 'user not found'}, status=status.HTTP_404_NOT_FOUND)
