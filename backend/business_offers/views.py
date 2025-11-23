from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from django.utils import timezone
from .models import BusinessOffer
from .serializers import (
    BusinessOfferSerializer, BusinessOfferCreateSerializer,
    BusinessOfferListSerializer
)
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class BusinessOfferViewSet(viewsets.ModelViewSet):
    """ViewSet for business offers"""
    queryset = BusinessOffer.objects.all()
    serializer_class = BusinessOfferSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.action == 'create':
            return BusinessOfferCreateSerializer
        elif self.action == 'list':
            return BusinessOfferListSerializer
        return BusinessOfferSerializer

    def get_queryset(self):
        queryset = BusinessOffer.objects.all()
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by company (for business users to see their own offers)
        if self.action == 'list' and self.request.user.is_authenticated:
            my_offers = self.request.query_params.get('my_offers')
            if my_offers == 'true':
                queryset = queryset.filter(company=self.request.user)
        
        # Filter only active offers for public
        if self.action == 'list' and not self.request.user.is_authenticated:
            today = timezone.now().date()
            queryset = queryset.filter(
                status='approved',
                valid_from__lte=today,
                valid_until__gte=today
            )
        
        return queryset

    @swagger_auto_schema(
        operation_summary='Получить активные предложения',
        operation_description='Возвращает список всех активных предложений от бизнеса',
        responses={
            200: openapi.Response('Список предложений', BusinessOfferListSerializer(many=True))
        },
        tags=['Предложения от бизнеса']
    )
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get all active business offers"""
        today = timezone.now().date()
        offers = BusinessOffer.objects.filter(
            status='approved',
            valid_from__lte=today,
            valid_until__gte=today
        ).order_by('-created_at')

        serializer = BusinessOfferListSerializer(offers, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary='Увеличить счетчик просмотров',
        operation_description='Увеличивает счетчик просмотров предложения',
        responses={
            200: openapi.Response('Просмотр засчитан'),
        },
        tags=['Предложения от бизнеса']
    )
    @action(detail=True, methods=['post'])
    def track_view(self, request, pk=None):
        """Track offer view"""
        offer = self.get_object()
        offer.views_count += 1
        offer.save(update_fields=['views_count'])
        return Response({'status': 'view tracked'})

    @swagger_auto_schema(
        operation_summary='Увеличить счетчик переходов',
        operation_description='Увеличивает счетчик переходов по предложению',
        responses={
            200: openapi.Response('Переход засчитан'),
        },
        tags=['Предложения от бизнеса']
    )
    @action(detail=True, methods=['post'])
    def track_click(self, request, pk=None):
        """Track offer click"""
        offer = self.get_object()
        offer.clicks_count += 1
        offer.save(update_fields=['clicks_count'])
        return Response({'status': 'click tracked'})

    def perform_create(self, serializer):
        """Override to set company from request user"""
        serializer.save(company=self.request.user)
