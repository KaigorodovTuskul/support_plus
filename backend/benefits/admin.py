from django.contrib import admin
from .models import Category, Region, Benefit, CommercialOffer, UserBenefitInteraction


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'icon']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ['name', 'code']
    search_fields = ['name', 'code']
    ordering = ['name']


@admin.register(Benefit)
class BenefitAdmin(admin.ModelAdmin):
    list_display = ['benefit_id', 'title', 'benefit_type', 'status', 'valid_from', 'valid_to', 'views_count']
    list_filter = ['benefit_type', 'status', 'applies_to_all_regions', 'valid_from']
    search_fields = ['benefit_id', 'title', 'description']
    filter_horizontal = ['regions', 'categories']
    readonly_fields = ['created_at', 'updated_at', 'last_verified', 'views_count', 'popularity_score']

    fieldsets = (
        ('Basic Information', {
            'fields': ('benefit_id', 'title', 'description', 'benefit_type')
        }),
        ('Target Audience', {
            'fields': ('target_groups', 'regions', 'applies_to_all_regions')
        }),
        ('Validity', {
            'fields': ('valid_from', 'valid_to', 'status')
        }),
        ('Requirements', {
            'fields': ('requirements', 'how_to_get', 'documents_needed')
        }),
        ('Source & Metadata', {
            'fields': ('source_url', 'last_verified', 'categories', 'views_count', 'popularity_score')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(CommercialOffer)
class CommercialOfferAdmin(admin.ModelAdmin):
    list_display = ['offer_id', 'title', 'partner_name', 'status', 'discount_description', 'valid_from', 'valid_to']
    list_filter = ['status', 'partner_category', 'applies_to_all_regions', 'valid_from']
    search_fields = ['offer_id', 'title', 'partner_name', 'description']
    filter_horizontal = ['regions', 'categories']
    readonly_fields = ['created_at', 'updated_at', 'views_count', 'popularity_score']


@admin.register(UserBenefitInteraction)
class UserBenefitInteractionAdmin(admin.ModelAdmin):
    list_display = ['user', 'interaction_type', 'benefit', 'offer', 'created_at']
    list_filter = ['interaction_type', 'created_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at']
