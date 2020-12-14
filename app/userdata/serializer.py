from rest_framework import serializers

from userdata.models import Wallet


class WalletSerializer(serializers.ModelSerializer):
    balance = serializers.FloatField()
    username = serializers.CharField(source='owner.username')

    class Meta:
        model = Wallet
        fields = ('pk', 'username', 'balance')


class CreateWalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ('owner', 'balance')

    def validate(self, attrs):
        if attrs['balance'] < 0.0:
            raise serializers.ValidationError('Balance cannot be negative')
        return attrs


class TransferSerializer(serializers.ModelSerializer):
    amount = serializers.FloatField()
    wallet_to = serializers.SerializerMethodField()

    class Meta:
        model = Wallet
        fields = ('amount', 'wallet_to')

    def validate(self, attrs):
        amount = attrs['amount']
        wallet_from = self.instance['wallet_from']
        wallet_to = Wallet.objects.filter(pk=self.instance.get('wallet_to')).first()

        if amount < 0:
            raise serializers.ValidationError('Balance cannot be negative')

        if amount > wallet_from.balance:
            raise serializers.ValidationError('Cannot transfer more than have')

        if not wallet_to or wallet_to.id == wallet_from.id:
            raise serializers.ValidationError('Bad wallet id')
        return attrs

    def get_wallet_to(self, instance):
        return Wallet.objects.filter(pk=instance.get('wallet_to')).first()
