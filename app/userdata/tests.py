from django.contrib.auth import get_user_model
from django.test import TestCase

from userdata.models import Wallet

User = get_user_model()
api_prefix = '/api/v0/wallets'

class WalletTestCase(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(username='admin',
                                         email='admin@some.random.domainfffm',
                                         password='random pass for polzovatel1!')
        Wallet.objects.create(_balance=1000, owner=self.admin)
        for user in ('user1', 'user2', 'user3'):
            u = User.objects.create_user(username=user,
                                         email=f'{user}@some.random.domainfffm',
                                         password='random pass for polzovatel1!')
            Wallet.objects.create(_balance=100, owner=u)

    def test_negative_balance(self):
        user = User.objects.get(username='user1')
        with self.assertRaises(ValueError):
            user_wallet = user.wallets.first()
            user_wallet.balance = -1

    def test_transfer(self):
        user1 = User.objects.get(username='user1')
        user1_wallet = user1.wallets.first()
        user2 = User.objects.get(username='user2')
        user2_wallet = user2.wallets.first()
        self.client.post(f'{api_prefix}/{user1_wallet.id}/transfer/{user2_wallet.id}/', {'amount': 10})
        user1_wallet.refresh_from_db()
        user2_wallet.refresh_from_db()
        self.assertEqual(user1_wallet.balance, 89.85)
        self.assertEqual(user2_wallet.balance, 110)

    def test_transfer_from_admin_without_fee(self):
        admin_wallet = self.admin.wallets.first()
        user = User.objects.get(username='user1')
        user_wallet = user.wallets.first()
        res = self.client.post(f'{api_prefix}/{admin_wallet.id}/transfer/{user_wallet.id}/', {'amount': 10})
        admin_wallet.refresh_from_db()
        user_wallet.refresh_from_db()
        self.assertEqual(admin_wallet.balance, 990)
        self.assertEqual(user_wallet.balance, 110)

    def test_transfer_negative_amount(self):
        user1 = User.objects.get(username='user1')
        user1_wallet = user1.wallets.first()
        user2 = User.objects.get(username='user2')
        user2_wallet = user2.wallets.first()
        user1_wallet.refresh_from_db()
        user2_wallet.refresh_from_db()
        res = self.client.post(f'{api_prefix}/{user1_wallet.id}/transfer/{user2_wallet.id}/', {'amount': -10})
        self.assertTrue(res.status_code == 400)

    def test_transfer_more_than_have(self):
        user1 = User.objects.get(username='user1')
        user1_wallet = user1.wallets.first()
        user2 = User.objects.get(username='user2')
        user2_wallet = user2.wallets.first()
        user1_wallet.refresh_from_db()
        user2_wallet.refresh_from_db()
        res = self.client.post(f'{api_prefix}/{user1_wallet.id}/transfer/{user2_wallet.id}/', {'amount': 110})
        self.assertTrue(res.status_code == 400)

    def test_send_all_funds(self):
        user1 = User.objects.get(username='user1')
        user1_wallet = user1.wallets.first()
        user2 = User.objects.get(username='user2')
        user2_wallet = user2.wallets.first()
        user1_wallet.refresh_from_db()
        user2_wallet.refresh_from_db()
        res = self.client.post(f'{api_prefix}/{user1_wallet.id}/transfer/{user2_wallet.id}/', {'amount': 100})
        self.assertTrue(res.status_code == 400)
