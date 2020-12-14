from django.conf import settings
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
        Wallet.objects.create(balance=1000, owner=self.admin)
        for user in ('user1', 'user2', 'user3'):
            u = User.objects.create_user(username=user,
                                         email=f'{user}@some.random.domainfffm',
                                         password='random pass for polzovatel1!')
            Wallet.objects.create(balance=100, owner=u)

    def test_transfer(self):
        admin_wallet = self.admin.wallets.first()
        old_balance_admin = admin_wallet.balance
        user1 = User.objects.get(username='user1')
        user1_wallet = user1.wallets.first()
        old_balance_wallet1 = user1_wallet.balance
        user2 = User.objects.get(username='user2')
        user2_wallet = user2.wallets.first()
        old_balance_wallet2 = user2_wallet.balance
        send_amount = 10
        self.client.post(f'{api_prefix}/{user1_wallet.id}/transfer/{user2_wallet.id}/', {'amount': send_amount})
        admin_wallet.refresh_from_db()
        user1_wallet.refresh_from_db()
        user2_wallet.refresh_from_db()
        fee = send_amount * settings.TRANSFER_FEE
        self.assertEqual(user1_wallet.balance, old_balance_wallet1 - send_amount - fee)
        self.assertEqual(user2_wallet.balance, old_balance_wallet2 + send_amount)
        self.assertEqual(admin_wallet.balance, old_balance_admin + fee)

    def test_transfer_from_admin_without_fee(self):
        admin_wallet = self.admin.wallets.first()
        old_balance_admin = admin_wallet.balance
        user = User.objects.get(username='user1')
        user_wallet = user.wallets.first()
        old_balance_user = user_wallet.balance
        send_amount = 10
        res = self.client.post(f'{api_prefix}/{admin_wallet.id}/transfer/{user_wallet.id}/', {'amount': send_amount})
        admin_wallet.refresh_from_db()
        user_wallet.refresh_from_db()
        self.assertEqual(admin_wallet.balance, old_balance_admin - send_amount)
        self.assertEqual(user_wallet.balance, old_balance_user + send_amount)

    def test_transfer_negative_amount(self):
        user1 = User.objects.get(username='user1')
        user1_wallet = user1.wallets.first()
        old_balance_wallet1 = user1_wallet.balance
        user2 = User.objects.get(username='user2')
        user2_wallet = user2.wallets.first()
        old_balance_wallet2 = user2_wallet.balance
        res = self.client.post(f'{api_prefix}/{user1_wallet.id}/transfer/{user2_wallet.id}/', {'amount': -10})
        self.assertTrue(res.status_code == 400)
        user1_wallet.refresh_from_db()
        user2_wallet.refresh_from_db()
        self.assertEqual(user1_wallet.balance, old_balance_wallet1)
        self.assertEqual(user2_wallet.balance, old_balance_wallet2)

    def test_transfer_more_than_have(self):
        user1 = User.objects.get(username='user1')
        user1_wallet = user1.wallets.first()
        old_balance_wallet1 = user1_wallet.balance
        user2 = User.objects.get(username='user2')
        user2_wallet = user2.wallets.first()
        old_balance_wallet2 = user2_wallet.balance
        res = self.client.post(f'{api_prefix}/{user1_wallet.id}/transfer/{user2_wallet.id}/', {'amount': old_balance_wallet1 + 10})
        self.assertTrue(res.status_code == 400)
        user1_wallet.refresh_from_db()
        user2_wallet.refresh_from_db()
        self.assertEqual(user1_wallet.balance, old_balance_wallet1)
        self.assertEqual(user2_wallet.balance, old_balance_wallet2)

    def test_transfer_to_myself(self):
        user1 = User.objects.get(username='user1')
        user1_wallet = user1.wallets.first()
        old_balance_wallet1 = user1_wallet.balance
        res = self.client.post(f'{api_prefix}/{user1_wallet.id}/transfer/{user1_wallet.id}/', {'amount': 10})
        self.assertTrue(res.status_code == 400)
        user1_wallet.refresh_from_db()
        self.assertEqual(user1_wallet.balance, old_balance_wallet1)

    def test_transfer_to_non_existent_wallet(self):
        user1 = User.objects.get(username='user1')
        user1_wallet = user1.wallets.first()
        old_balance_wallet1 = user1_wallet.balance
        wallet_id = 5
        non_existtent_wallet = Wallet.objects.filter(pk=wallet_id)
        while non_existtent_wallet.exists():
            wallet_id += 1
            non_existtent_wallet = Wallet.objects.filter(pk=wallet_id)
        res = self.client.post(f'{api_prefix}/{user1_wallet.id}/transfer/{user1_wallet.id}/', {'amount': 10})
        self.assertTrue(res.status_code == 400)
        user1_wallet.refresh_from_db()
        self.assertEqual(user1_wallet.balance, old_balance_wallet1)
