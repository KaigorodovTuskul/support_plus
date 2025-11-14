from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserProfile, VerificationRequest


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'beneficiary_category', 'region', 'is_verified', 'created_at']
    list_filter = ['is_verified', 'beneficiary_category', 'region', 'is_staff']
    search_fields = ['username', 'email', 'region']

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Beneficiary Information', {
            'fields': ('phone', 'beneficiary_category', 'region', 'snils', 'is_verified', 'verification_date')
        }),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'font_size', 'color_mode', 'speech_assistant_enabled', 'updated_at']
    list_filter = ['font_size', 'color_mode', 'show_images']
    search_fields = ['user__username', 'user__email']


@admin.register(VerificationRequest)
class VerificationRequestAdmin(admin.ModelAdmin):
    list_display = ['user', 'status', 'created_at', 'reviewed_at', 'reviewed_by']
    list_filter = ['status', 'created_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
