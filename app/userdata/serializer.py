from rest_framework import serializers

from userdata.models import Wallet


class WalletSerializer(serializers.ModelSerializer):
    balance = serializers.FloatField()
    username = serializers.CharField(source='owner.username')

    class Meta:
        model = Wallet
        fields = ('pk', 'username', 'balance')


class CreateWalletSerializer(serializers.ModelSerializer):
    balance = serializers.FloatField()

    class Meta:
        model = Wallet
        fields = ('owner', 'balance')
