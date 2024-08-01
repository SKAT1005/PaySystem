from django.contrib import admin

from .models import Balance, Transaction

@admin.register(Balance)
class BalanceAdmin(admin.ModelAdmin):
    pass
