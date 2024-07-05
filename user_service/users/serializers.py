from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password


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
    

class UserPersonalInfoSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(max_length=100, required=False)
    last_name = serializers.CharField(max_length=100, required=False)
    class Meta:
        model = get_user_model()
        fields = ['profile_picture', 'first_name', 'last_name',
                  'about_self', 'categories_liked']
        

class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ConfirmationCodeSerializer(serializers.Serializer):
    code = serializers.IntegerField(min_value=100000, max_value=999999)


class EmailWithConfirmationCodeSerializer(EmailSerializer, ConfirmationCodeSerializer):
    pass


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True,
                                         validators=[validate_password])
    
    def validate_old_password(self, value):
        user_email = self.context['request'].user
        user = get_user_model().objects.get(email=user_email)
        if not user.check_password(value):
            raise serializers.ValidationError('Введённый текущий пароль неверный')
        return value
    
    def validate(self, attrs):
        if attrs['old_password'] == attrs['new_password']:
            raise serializers.ValidationError(
                'Новый пароль не может совпадать со старым паролем'
            )
        return attrs
    
    def save(self, **kwargs):
        user_email = self.context['request'].user
        user = get_user_model().objects.get(email=user_email)
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user