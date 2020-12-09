from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models

UserModel = get_user_model()


class Wallet(models.Model):
    _balance = models.FloatField(default=0.0)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="wallets"
    )

    @property
    def balance(self):
        if self._balance:
            return self._balance
        return 0

    @balance.setter
    def balance(self, value):
        if value < 0:
            raise ValueError('Balance cannot go below zero')
        self._balance = value

    def transfer(self, amount, to_wallet):
        admin = UserModel.objects.get(username='admin')
        admin_wallet = admin.wallets.first()

        fee = amount * 0.015
        if self.id == admin_wallet.id:
            fee = 0

        self.balance -= amount + fee
        to_wallet.balance += amount
        admin_wallet.balance += fee

        admin_wallet.save()
        to_wallet.save()
        self.save()
