from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.utils import timezone
from .models import Donation
from .serializers import (
    DonationSerializer, DonationCreateSerializer,
    DonationConfirmSerializer, LeaderboardSerializer
)
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class DonationViewSet(viewsets.ModelViewSet):
    """ViewSet for donations"""
    queryset = Donation.objects.all()
    serializer_class = DonationSerializer
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if self.action == 'create':
            return DonationCreateSerializer
        return DonationSerializer

    @swagger_auto_schema(
        operation_summary='Получить донат по transaction_id',
        operation_description='Возвращает информацию о донате по ID транзакции',
        manual_parameters=[
            openapi.Parameter('transaction_id', openapi.IN_QUERY, description="ID транзакции", type=openapi.TYPE_STRING, required=True)
        ],
        responses={
            200: openapi.Response('Донат найден', DonationSerializer),
            404: openapi.Response('Донат не найден'),
        },
        tags=['Пожертвования']
    )
    @action(detail=False, methods=['get'])
    def by_transaction(self, request):
        """Get donation by transaction_id"""
        transaction_id = request.query_params.get('transaction_id')

        if not transaction_id:
            return Response(
                {'error': 'transaction_id обязателен'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            donation = Donation.objects.get(transaction_id=transaction_id)
            return Response(
                DonationSerializer(donation).data,
                status=status.HTTP_200_OK
            )
        except Donation.DoesNotExist:
            return Response(
                {'error': 'Транзакция не найдена'},
                status=status.HTTP_404_NOT_FOUND
            )

    @swagger_auto_schema(
        operation_summary='Получить лидерборд донатов',
        operation_description='Возвращает список всех оплаченных пожертвований для отображения в лидерборде',
        responses={
            200: openapi.Response('Список донатов', LeaderboardSerializer(many=True))
        },
        tags=['Пожертвования']
    )
    @action(detail=False, methods=['get'])
    def leaderboard(self, request):
        """Get leaderboard of donations"""
        donations = Donation.objects.filter(
            payment_status='paid',
            show_on_leaderboard=True
        ).order_by('-amount', '-created_at')

        serializer = LeaderboardSerializer(donations, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary='Подтвердить оплату',
        operation_description='Подтверждает оплату пожертвования (mock)',
        request_body=DonationConfirmSerializer,
        responses={
            200: openapi.Response('Оплата подтверждена', DonationSerializer),
            400: openapi.Response('Ошибка'),
        },
        tags=['Пожертвования']
    )
    @action(detail=False, methods=['post'])
    def confirm_payment(self, request):
        """Confirm payment (mock)"""
        serializer = DonationConfirmSerializer(data=request.data)

        if serializer.is_valid():
            transaction_id = serializer.validated_data['transaction_id']

            try:
                donation = Donation.objects.get(transaction_id=transaction_id)
                donation.payment_status = 'paid'
                donation.payment_date = timezone.now()
                donation.save()

                return Response(
                    DonationSerializer(donation).data,
                    status=status.HTTP_200_OK
                )
            except Donation.DoesNotExist:
                return Response(
                    {'error': 'Транзакция не найдена'},
                    status=status.HTTP_404_NOT_FOUND
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary='Получить статистику пожертвований',
        operation_description='Возвращает общую статистику по пожертвованиям',
        responses={
            200: openapi.Response(
                'Статистика',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'total_amount': openapi.Schema(type=openapi.TYPE_NUMBER),
                        'total_donations': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'gold_partners': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'silver_partners': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'bronze_partners': openapi.Schema(type=openapi.TYPE_INTEGER),
                    }
                )
            )
        },
        tags=['Пожертвования']
    )
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get donation statistics"""
        paid_donations = Donation.objects.filter(payment_status='paid')

        total_amount = sum(d.amount for d in paid_donations)
        total_donations = paid_donations.count()
        gold_partners = paid_donations.filter(tier='gold').count()
        silver_partners = paid_donations.filter(tier='silver').count()
        bronze_partners = paid_donations.filter(tier='bronze').count()

        return Response({
            'total_amount': float(total_amount),
            'total_donations': total_donations,
            'gold_partners': gold_partners,
            'silver_partners': silver_partners,
            'bronze_partners': bronze_partners,
        })
