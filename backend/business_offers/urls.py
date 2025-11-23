from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BusinessOfferViewSet

router = DefaultRouter()
router.register(r'offers', BusinessOfferViewSet, basename='business-offer')

urlpatterns = [
    path('', include(router.urls)),
]
