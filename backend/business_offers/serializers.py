from rest_framework import serializers
from .models import BusinessOffer
from users.models import User


class BusinessOfferSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.company_name', read_only=True)
    is_active = serializers.SerializerMethodField()

    class Meta:
        model = BusinessOffer
        fields = [
            'id', 'title', 'description', 'category', 'discount_percentage',
            'company', 'company_name', 'company_logo_url', 'contact_phone',
            'contact_email', 'website_url', 'target_regions', 'target_categories',
            'valid_from', 'valid_until', 'status', 'rejection_reason',
            'created_at', 'updated_at', 'views_count', 'clicks_count', 'is_active'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'views_count', 'clicks_count', 'status', 'rejection_reason']

    def get_is_active(self, obj):
        return obj.is_active()


class BusinessOfferCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating business offers"""

    class Meta:
        model = BusinessOffer
        fields = [
            'title', 'description', 'category', 'discount_percentage',
            'company_logo_url', 'contact_phone', 'contact_email', 'website_url',
            'target_regions', 'target_categories', 'valid_from', 'valid_until'
        ]

    def create(self, validated_data):
        # Set company from request user
        user = self.context['request'].user
        validated_data['company'] = user
        validated_data['status'] = 'pending'
        return super().create(validated_data)


class BusinessOfferListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing offers"""
    company_name = serializers.CharField(source='company.company_name', read_only=True)
    is_active = serializers.SerializerMethodField()

    class Meta:
        model = BusinessOffer
        fields = [
            'id', 'title', 'category', 'discount_percentage', 'company_name',
            'company_logo_url', 'valid_from', 'valid_until', 'status', 'is_active'
        ]

    def get_is_active(self, obj):
        return obj.is_active()
