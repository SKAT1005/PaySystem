from decimal import Decimal

from django.db import transaction

from .models import Balance, Transaction, TransactionType


def topup_balance(user, amount):
    balance = Balance.objects.get(user=user)
    balance.amount += amount
    balance.save(update_fields=['amount'])

    Transaction.objects.create(
        user=user,
        amount=amount,
        type=TransactionType.TOPUP,
    )

def transfer_balance(sender, receiver, amount):
    if amount <= 0:
        raise ValueError('Сумма перевода должна быть положительной.')

    sender_balance = Balance.objects.get(user=sender)
    if sender_balance.amount < amount:
        raise ValueError('Недостаточно средств.')

    with transaction.atomic():
        sender_balance.amount -= amount
        sender_balance.save(update_fields=['amount'])

        receiver_balance = Balance.objects.get(user=receiver)
        receiver_balance.amount += amount
        receiver_balance.save(update_fields=['amount'])

        Transaction.objects.create(
            user=sender,
            amount=amount,
            type=TransactionType.TRANSFER,
            description=f'Перевод на баланс пользователя {receiver.username}',
        )

        Transaction.objects.create(
            user=receiver,
            amount=amount,
            type=TransactionType.TOPUP,
            description=f'Перевод от пользователя {sender.username}',
        )
