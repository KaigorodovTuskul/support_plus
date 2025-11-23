from django.contrib import admin
from .models import BusinessOffer


@admin.register(BusinessOffer)
class BusinessOfferAdmin(admin.ModelAdmin):
    list_display = ['title', 'company', 'category', 'status', 'valid_from', 'valid_until', 'views_count', 'clicks_count']
    list_filter = ['status', 'category', 'valid_from', 'valid_until']
    search_fields = ['title', 'description', 'company__company_name']
    readonly_fields = ['created_at', 'updated_at', 'views_count', 'clicks_count']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'description', 'category', 'discount_percentage')
        }),
        ('Компания', {
            'fields': ('company', 'company_logo_url', 'contact_phone', 'contact_email', 'website_url')
        }),
        ('Целевая аудитория', {
            'fields': ('target_regions', 'target_categories')
        }),
        ('Период действия', {
            'fields': ('valid_from', 'valid_until')
        }),
        ('Статус', {
            'fields': ('status', 'rejection_reason', 'approved_at', 'approved_by')
        }),
        ('Статистика', {
            'fields': ('views_count', 'clicks_count', 'created_at', 'updated_at')
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if obj.status == 'approved' and not obj.approved_at:
            from django.utils import timezone
            obj.approved_at = timezone.now()
            obj.approved_by = request.user
        super().save_model(request, obj, form, change)
