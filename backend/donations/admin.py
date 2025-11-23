from django.contrib import admin
from .models import Donation


@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ['get_donor_display_name', 'amount', 'donor_type', 'tier', 'payment_status', 'created_at']
    list_filter = ['donor_type', 'tier', 'payment_status', 'is_anonymous']
    search_fields = ['donor_name', 'company_name', 'contact_email', 'transaction_id']
    readonly_fields = ['created_at', 'updated_at', 'transaction_id']

    fieldsets = (
        ('Информация о доноре', {
            'fields': ('donor_type', 'donor_name', 'company_name', 'company_address', 'contact_email', 'contact_phone', 'logo_url')
        }),
        ('Детали пожертвования', {
            'fields': ('amount', 'is_anonymous', 'tier', 'message', 'show_on_leaderboard')
        }),
        ('Платежная информация', {
            'fields': ('payment_status', 'payment_date', 'transaction_id')
        }),
        ('Метаданные', {
            'fields': ('created_at', 'updated_at')
        }),
    )
