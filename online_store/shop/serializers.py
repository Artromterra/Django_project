from rest_framework import serializers

from .models.order import Order

class PaymentSerializer(serializers.Serializer):
    order_id = serializers.IntegerField()
    card_number = serializers.CharField(max_length=16)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2)
