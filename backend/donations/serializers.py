from rest_framework import serializers
from .models import Donation
import uuid
from django.utils import timezone


class DonationSerializer(serializers.ModelSerializer):
    display_name = serializers.SerializerMethodField()

    class Meta:
        model = Donation
        fields = [
            'id', 'donor_type', 'donor_name', 'company_name', 'company_address',
            'contact_email', 'contact_phone', 'logo_url', 'amount', 'is_anonymous',
            'tier', 'message', 'payment_status', 'payment_date', 'transaction_id',
            'created_at', 'show_on_leaderboard', 'display_name'
        ]
        read_only_fields = ['id', 'tier', 'payment_status', 'payment_date', 'transaction_id', 'created_at']

    def get_display_name(self, obj):
        return obj.get_donor_display_name()

    def create(self, validated_data):
        # Generate unique transaction ID
        validated_data['transaction_id'] = f'TXN-{uuid.uuid4().hex[:12].upper()}'
        return super().create(validated_data)


class DonationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating donations"""

    class Meta:
        model = Donation
        fields = [
            'donor_type', 'donor_name', 'company_name', 'company_address',
            'contact_email', 'contact_phone', 'logo_url', 'amount',
            'is_anonymous', 'message', 'show_on_leaderboard'
        ]

    def validate(self, attrs):
        # Check if anonymous
        is_anonymous = attrs.get('is_anonymous', False)

        if not is_anonymous:
            # If not anonymous, require at least donor_name or company_name
            if not attrs.get('donor_name') and not attrs.get('company_name'):
                attrs['is_anonymous'] = True

        return attrs

    def create(self, validated_data):
        # Generate unique transaction ID
        validated_data['transaction_id'] = f'TXN-{uuid.uuid4().hex[:12].upper()}'
        validated_data['payment_status'] = 'pending'
        return super().create(validated_data)


class DonationConfirmSerializer(serializers.Serializer):
    """Serializer for confirming payment"""
    transaction_id = serializers.CharField(max_length=100)

    def validate_transaction_id(self, value):
        try:
            donation = Donation.objects.get(transaction_id=value)
            if donation.payment_status == 'paid':
                raise serializers.ValidationError('Эта транзакция уже оплачена')
        except Donation.DoesNotExist:
            raise serializers.ValidationError('Транзакция не найдена')
        return value


class LeaderboardSerializer(serializers.ModelSerializer):
    """Serializer for leaderboard display"""
    display_name = serializers.SerializerMethodField()

    class Meta:
        model = Donation
        fields = ['display_name', 'amount', 'tier', 'logo_url', 'message', 'created_at']

    def get_display_name(self, obj):
        return obj.get_donor_display_name()
