from django.conf import settings
from django.contrib.auth import get_user_model


class WalletManager:
    def transfer(self, from_, to, amount):
        admin = get_user_model().objects.get(username='admin')
        admin_wallet = admin.wallets.first()

        fee = amount * settings.TRANSFER_FEE
        if from_.id == admin_wallet.id:
            fee = 0

        from_.balance -= amount + fee
        to.balance += amount
        admin_wallet.balance += fee

        admin_wallet.save()
        to.save()
        from_.save()
