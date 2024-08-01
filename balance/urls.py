from django.urls import path
from .views import TopupBalanceView, TransferBalanceView, GetBalanceView, GetHistoryView

urlpatterns = [
    path('topup/', TopupBalanceView.as_view(), name='topup_balance'),
    path('transfer/', TransferBalanceView.as_view(), name='transfer_balance'),
    path('history/', GetHistoryView.as_view(), name='history'),
    path('', GetBalanceView.as_view(), name='get_balance'),
]
