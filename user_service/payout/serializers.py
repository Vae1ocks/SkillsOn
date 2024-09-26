from rest_framework import serializers
from .models import UserPayout


class UserPayoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPayout
        fields = ["id", "value", "status", "created", "updated"]
