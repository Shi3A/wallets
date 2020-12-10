from django.db import transaction

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from userdata.models import Wallet
from userdata.serializer import WalletSerializer, CreateWalletSerializer


class WalletView(viewsets.ModelViewSet):

    serializer_class = WalletSerializer
    queryset = Wallet.objects

    def get_serializer_class(self):
        serializer_class = self.serializer_class
        if self.request.method == 'POST':
            serializer_class = CreateWalletSerializer
        return serializer_class

    @action(detail=True, methods=['post'], url_path='transfer/(?P<to_pk>[^/.]+)')
    def transfer(self, request, pk=None, *args, **kwargs):
        if pk == kwargs["to_pk"]:
            return Response('Bad wallet id', status=400)

        wallet = self.get_object()

        amount = float(request.data.get('amount', 0))
        wallet_to = Wallet.objects.filter(pk=kwargs["to_pk"]).first()

        if not wallet_to:
            return Response('Bad wallet id', status=400)

        if amount < 0:
            return Response('Balance cannot be negative', status=400)

        try:
            with transaction.atomic():
                wallet.transfer(amount, wallet_to)
        except:
            return Response('bad amount', status=400)
        return Response('ok')
