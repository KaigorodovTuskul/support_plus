from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import DonationViewSet

router = DefaultRouter()
router.register(r'donations', DonationViewSet, basename='donation')  # ← ДОБАВЬ ЭТУ СТРОЧКУ

urlpatterns = [
    path('', include(router.urls)),
]
