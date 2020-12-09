from rest_framework.routers import DefaultRouter

from userdata.views import WalletView

router = DefaultRouter()
router.register(r'wallets', WalletView, basename='tasks')

urlpatterns = router.urls
