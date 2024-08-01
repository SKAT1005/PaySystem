from django.db import models
from django.contrib.auth.models import AbstractUser, User


# class User(AbstractUser):
#     pass

class Balance(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=10, choices=(('topup', 'Пополнение'), ('transfer', 'Перевод'),))
    description = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.type} - {self.amount} рублей"
