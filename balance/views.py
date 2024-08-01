import decimal

from django.contrib.auth.models import User
from rest_framework import views, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import BalanceSerializer, TransactionSerializer
from .models import Balance, Transaction

# {'amount': 100}
# {"amount": 100, "receiver_id": "1"}


class TopupBalanceView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        amount = request.data.get('amount')
        if not amount:
            return Response({'error': 'Не указана сумма.'}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        balance = Balance.objects.get(user=user)
        balance.amount += decimal.Decimal(amount)  # Преобразование копеек в рубли
        balance.save()

        transaction = Transaction.objects.create(
            user=user,
            amount=decimal.Decimal(amount),
            type='topup',
            description='Пополнение баланса',
        )

        return Response({'message': 'Баланс пополнен.'}, status=status.HTTP_200_OK)

class TransferBalanceView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        receiver_id = request.data.get('receiver_id')
        amount = request.data.get('amount')
        if not receiver_id or not amount:
            return Response({'error': 'Не указаны данные получателя или сумма.'}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        receiver = User.objects.get(id=receiver_id)
        if not receiver:
            return Response({'error': 'Пользователь не найден.'}, status=status.HTTP_404_NOT_FOUND)

        balance = Balance.objects.get(user=user)
        if balance.amount < decimal.Decimal(amount):
            return Response({'error': 'Недостаточно средств.'}, status=status.HTTP_400_BAD_REQUEST)

        balance.amount -= decimal.Decimal(amount)
        balance.save()

        receiver_balance = Balance.objects.get(user=receiver)
        receiver_balance.amount += decimal.Decimal(amount)
        receiver_balance.save()

        transaction = Transaction.objects.create(
            user=user,
            amount=decimal.Decimal(amount),
            type='transfer',
            description=f'Перевод на баланс пользователя {receiver.username}',
        )

        receiver_transaction = Transaction.objects.create(
            user=receiver,
            amount=decimal.Decimal(amount),
            type='topup',
            description=f'Перевод от пользователя {user.username}',
        )

        return Response({'message': 'Перевод выполнен.'}, status=status.HTTP_200_OK)

class GetBalanceView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        balance = Balance.objects.get(user=user).amount
        return Response({'balance': balance}, status=status.HTTP_200_OK)


class GetHistoryView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        history = Transaction.objects.filter(user=user).order_by('-timestamp')
        serializer = TransactionSerializer(history, many=True)

        return Response({'history': serializer.data}, status=status.HTTP_200_OK)