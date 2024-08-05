from decimal import Decimal
from unittest.mock import MagicMock, patch

from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate

from .models import Balance, Transaction, TransactionType
from .serializers import BalanceSerializer, TransactionSerializer
from .services import topup_balance, transfer_balance
from .views import (GetBalanceView, GetHistoryView, TopupBalanceView,
                    TransferBalanceView)


class BalanceTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.balance = Balance.objects.create(user=self.user, amount=Decimal('100.00'))

    def test_topup_balance_view(self):
        request = self.factory.post('/topup/', {'amount': '50.00'}, format='json')
        force_authenticate(request, user=self.user)
        view = TopupBalanceView.as_view()
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'message': 'Баланс пополнен.'})
        self.balance.refresh_from_db()
        self.assertEqual(self.balance.amount, Decimal('150.00'))

    def test_topup_balance_view_invalid_amount(self):
        request = self.factory.post('/topup/', {'amount': 'invalid'}, format='json')
        force_authenticate(request, user=self.user)
        view = TopupBalanceView.as_view()
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'error': 'Неверный формат суммы.'})

    def test_transfer_balance_view(self):
        receiver = User.objects.create_user(username='receiver', password='testpassword')
        Balance.objects.create(user=receiver)
        request = self.factory.post('/transfer/', {'receiver_id': receiver.id, 'amount': '25.00'}, format='json')
        force_authenticate(request, user=self.user)
        view = TransferBalanceView.as_view()
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'message': 'Перевод выполнен.'})
        self.balance.refresh_from_db()
        self.assertEqual(self.balance.amount, Decimal('75.00'))

        receiver_balance = Balance.objects.get(user=receiver)
        self.assertEqual(receiver_balance.amount, Decimal('25.00'))
    def test_transfer_balance_view_invalid_receiver(self):
        request = self.factory.post('/transfer/', {'receiver_id': 12345, 'amount': '25.00'}, format='json')
        force_authenticate(request, user=self.user)
        view = TransferBalanceView.as_view()
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, {'error': 'Пользователь не найден.'})

    def test_transfer_balance_view_invalid_amount(self):
        receiver = User.objects.create_user(username='receiver', password='testpassword')
        request = self.factory.post('/transfer/', {'receiver_id': receiver.id, 'amount': 'invalid'}, format='json')
        force_authenticate(request, user=self.user)
        view = TransferBalanceView.as_view()
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'error': 'Неверный формат суммы.'})

    def test_get_balance_view(self):
        request = self.factory.get('/')
        force_authenticate(request, user=self.user)
        view = GetBalanceView.as_view()
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'amount': '100.00'})

    def test_get_history_view(self):
        transaction = Transaction.objects.create(user=self.user, amount=Decimal('50.00'), type=TransactionType.TOPUP)
        request = self.factory.get('/history/')
        force_authenticate(request, user=self.user)
        view = GetHistoryView.as_view()
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['amount'], '50.00')

    @patch('balance_app.services.topup_balance')
    def test_topup_balance_service(self, mock_topup_balance):
        mock_topup_balance.return_value = None
        topup_balance(self.user, Decimal('50.00'))

        mock_topup_balance.assert_called_once_with(self.user, Decimal('50.00'))

    @patch('balance_app.services.transfer_balance')
    def test_transfer_balance_service(self, mock_transfer_balance):
        receiver = User.objects.create_user(username='receiver', password='testpassword')
        mock_transfer_balance.return_value = None
        transfer_balance(self.user, receiver, Decimal('25.00'))

        mock_transfer_balance.assert_called_once_with(self.user, receiver, Decimal('25.00'))

    @patch('balance_app.services.transfer_balance')
    def test_transfer_balance_service_invalid_amount(self, mock_transfer_balance):
        receiver = User.objects.create_user(username='receiver', password='testpassword')
        mock_transfer_balance.side_effect = ValueError('Сумма перевода должна быть положительной.')

        with self.assertRaises(ValueError):
            transfer_balance(self.user, receiver, Decimal('-25.00'))

        mock_transfer_balance.assert_called_once_with(self.user, receiver, Decimal('-25.00'))
