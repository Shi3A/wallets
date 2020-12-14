from django.db import transaction

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from userdata.manager import WalletManager
from userdata.models import Wallet
from userdata.serializer import WalletSerializer, CreateWalletSerializer, TransferSerializer


class WalletView(viewsets.ModelViewSet):

    serializer_class = WalletSerializer
    queryset = Wallet.objects

    def get_serializer_class(self):
        serializer_class = self.serializer_class
        if self.action == 'transfer':
            serializer_class = TransferSerializer
        elif self.request.method == 'POST':
            serializer_class = CreateWalletSerializer
        return serializer_class

    @action(detail=True, methods=['post'], url_path='transfer/(?P<to_pk>[^/.]+)')
    def transfer(self, request, pk=None, *args, **kwargs):
        wallet_from = self.get_object()
        instance = {'wallet_from': wallet_from,
                    'wallet_to': kwargs["to_pk"],
                    'amount': request.data.get('amount')
                    }
        serializer = TransferSerializer(instance=instance, data=request.data)
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    WalletManager().tranfser(wallet_from, serializer.data['wallet_to'], serializer.data['amount'])
                    res = Response('ok')
            except:
                res = Response('Error occurred', status=500)
        else:
            res = Response(f'validation failed: {serializer.errors}', status=400)
        return res
