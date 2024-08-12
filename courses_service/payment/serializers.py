from rest_framework import serializers
from .models import Order


class OrderSerializer(serializers.ModelSerializer):
    price = serializers.DecimalField(max_digits=10, decimal_places=2,
                                     required=False)

    class Meta:
        model = Order
        fields = ['id', 'course', 'price', 'created', 'completed']
