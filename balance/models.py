from django.contrib.auth.models import AbstractUser, User
from django.db import models


class TransactionType(models.TextChoices):
    TOPUP = "topup", "Пополнение"
    TRANSFER = "transfer", "Перевод"


class Balance(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, verbose_name="Пользователь"
    )
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="Баланс пользователя"
    )


class Transaction(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="Пользователь"
    )
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Сумма операции"
    )
    timestamp = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата и время операции"
    )
    type = models.CharField(
        max_length=10, choices=TransactionType.choices, verbose_name="Тип операции"
    )
    description = models.CharField(
        max_length=255, blank=True, verbose_name="Описание операции"
    )

    def __str__(self):
        return f"{self.type} - {self.amount} рублей"
