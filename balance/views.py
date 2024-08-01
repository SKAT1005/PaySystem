import decimal
from django.db import transaction

from django.contrib.auth.models import User
from rest_framework import views, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import RetrieveAPIView, ListAPIView
from rest_framework.pagination import PageNumberPagination

from .serializers import BalanceSerializer, TransactionSerializer
from .models import Balance, Transaction
from .services import topup_balance, transfer_balance


class TopupBalanceView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        amount = request.data.get('amount')
        if not amount:
            return Response({'error': 'Не указана сумма.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            amount = decimal.Decimal(amount)
        except decimal.InvalidOperation:
            return Response({'error': 'Неверный формат суммы.'}, status=status.HTTP_400_BAD_REQUEST)

        # Вызов сервиса для пополнения баланса
        topup_balance(request.user, amount)

        return Response({'message': 'Баланс пополнен.'})

class TransferBalanceView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        receiver_id = request.data.get('receiver_id')
        amount = request.data.get('amount')
        if not receiver_id or not amount:
            return Response({'error': 'Не указаны данные получателя или сумма.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            amount = decimal.Decimal(amount)
        except decimal.InvalidOperation:
            return Response({'error': 'Неверный формат суммы.'}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        receiver = User.objects.filter(id=receiver_id).first()
        if not receiver:
            return Response({'error': 'Пользователь не найден.'}, status=status.HTTP_404_NOT_FOUND)

        try:
            transfer_balance(user, receiver, amount)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'message': 'Перевод выполнен.'})

class GetBalanceView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BalanceSerializer

    def get_object(self):
        return Balance.objects.get(user=self.request.user)

class GetHistoryView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TransactionSerializer
    pagination_class = PageNumberPagination

    def get_queryset(self):
        user = self.request.user
        return Transaction.objects.filter(user=user).order_by('-timestamp')
