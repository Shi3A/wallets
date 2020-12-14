from django.conf import settings
from django.db import models


class Wallet(models.Model):
    balance = models.FloatField(default=0.0)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="wallets"
    )
