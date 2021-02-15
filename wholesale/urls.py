from django.conf.urls import include
from django.urls.conf import path
from wholesale.views import ProductAPIView, PurchaseAPIView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'product', ProductAPIView)
router.register(r'purchase', PurchaseAPIView)

urlpatterns = [
    path('', include(router.urls)),
]
