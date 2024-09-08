from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from django.contrib.auth import get_user_model

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password']
        extra_kwargs = {'password': {'write_only' : True}}
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data, password=password)
        return user


class ConfirmationCodeSerializer(serializers.Serializer):
    code = serializers.IntegerField(min_value=100000, max_value=999999)


class CategorySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    # title = serializers.CharField(max_length=150)


class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['password']


class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name
        return token
