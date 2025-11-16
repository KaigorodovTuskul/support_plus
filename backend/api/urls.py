from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

router = DefaultRouter()
router.register(r'benefits', views.BenefitViewSet, basename='benefit')
router.register(r'offers', views.CommercialOfferViewSet, basename='offer')
router.register(r'categories', views.CategoryViewSet, basename='category')
router.register(r'regions', views.RegionViewSet, basename='region')
router.register(r'profile', views.UserProfileViewSet, basename='profile')

urlpatterns = [
    # Auth endpoints
    path('auth/register/', views.register_user, name='register'),
    path('auth/login/', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/oauth/gosuslugi/', views.mock_oauth_login, name='oauth_gosuslugi'),
    path('auth/me/', views.user_info, name='user_info'),
    path('auth/change-password/', views.change_password, name='change_password'),

    # Export
    path('export/benefits/pdf/', views.export_benefits_pdf, name='export_pdf'),

    # Router URLs
    path('', include(router.urls)),
]
