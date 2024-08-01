from rest_framework import serializers
from .models import Balance, Transaction


class BalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Balance
        fields = ['amount']

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'