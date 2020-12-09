from django.contrib import admin

from userdata.models import Wallet


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    pass
