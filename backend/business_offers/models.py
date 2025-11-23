from django.db import models
from django.core.validators import MinValueValidator
from users.models import User


class BusinessOffer(models.Model):
    """Business offers/promotions from companies"""

    STATUS_CHOICES = [
        ('pending', 'Ожидает модерации'),
        ('approved', 'Одобрено'),
        ('rejected', 'Отклонено'),
        ('expired', 'Истекло'),
    ]

    CATEGORY_CHOICES = [
        ('discount', 'Скидка'),
        ('service', 'Услуга'),
        ('product', 'Товар'),
        ('event', 'Мероприятие'),
        ('other', 'Другое'),
    ]

    # Offer details
    title = models.CharField(max_length=255, verbose_name='Название акции')
    description = models.TextField(verbose_name='Описание')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='discount', verbose_name='Категория')
    discount_percentage = models.IntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
        verbose_name='Процент скидки'
    )
    
    # Company info
    company = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='business_offers',
        limit_choices_to={'user_type__in': ['company', 'ip', 'self_employed']},
        verbose_name='Компания'
    )
    company_logo_url = models.URLField(blank=True, null=True, verbose_name='URL логотипа')
    contact_phone = models.CharField(max_length=20, blank=True, verbose_name='Телефон для связи')
    contact_email = models.EmailField(blank=True, verbose_name='Email для связи')
    website_url = models.URLField(blank=True, null=True, verbose_name='Сайт')
    
    # Target audience
    target_regions = models.JSONField(default=list, blank=True, verbose_name='Целевые регионы')
    target_categories = models.JSONField(default=list, blank=True, verbose_name='Целевые категории льготников')
    
    # Validity
    valid_from = models.DateField(verbose_name='Действует с')
    valid_until = models.DateField(verbose_name='Действует до')
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Статус')
    rejection_reason = models.TextField(blank=True, null=True, verbose_name='Причина отклонения')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    approved_at = models.DateTimeField(blank=True, null=True, verbose_name='Дата одобрения')
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_offers',
        verbose_name='Кем одобрено'
    )
    
    # Statistics
    views_count = models.IntegerField(default=0, verbose_name='Количество просмотров')
    clicks_count = models.IntegerField(default=0, verbose_name='Количество переходов')

    class Meta:
        db_table = 'business_offers'
        verbose_name = 'Предложение от бизнеса'
        verbose_name_plural = 'Предложения от бизнеса'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} - {self.company.company_name}'

    def is_active(self):
        """Check if offer is currently active"""
        from django.utils import timezone
        today = timezone.now().date()
        return (
            self.status == 'approved' and
            self.valid_from <= today <= self.valid_until
        )
