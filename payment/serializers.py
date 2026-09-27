from rest_framework import serializers

from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ["id", "session", "amount", "method", "status", "reference", "paid_at"]
        read_only_fields = fields