from rest_framework import serializers
from django.contrib.auth import get_user_model


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = ['email', 'first_name', 'last_name',
                  'profile_picture', 'about_self', 'categories_liked',
                  'password']
        extra_kwargs = {'password': {'write_only' : True}}
        
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = get_user_model().objects.create_user(**validated_data, password=password)
        return user