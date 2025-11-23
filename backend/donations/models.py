from django.db import models
from django.core.validators import MinValueValidator


class Donation(models.Model):
    """Donation model for tracking donations from individuals and companies"""

    DONOR_TYPE_CHOICES = [
        ('individual', 'Частное лицо'),
        ('company', 'Компания'),
        ('ip', 'ИП'),
        ('self_employed', 'Самозанятый'),
    ]

    TIER_CHOICES = [
        ('bronze', 'Бронзовый партнер'),
        ('silver', 'Серебряный партнер'),
        ('gold', 'Золотой партнер'),
        ('none', 'Без статуса'),
    ]

    # Donor information
    donor_type = models.CharField(max_length=20, choices=DONOR_TYPE_CHOICES, default='individual')
    donor_name = models.CharField(max_length=255, blank=True, null=True, verbose_name='Имя донора')
    company_name = models.CharField(max_length=255, blank=True, null=True, verbose_name='Название компании')
    company_address = models.TextField(blank=True, null=True, verbose_name='Адрес компании')
    contact_email = models.EmailField(blank=True, null=True, verbose_name='Email для связи')
    contact_phone = models.CharField(max_length=20, blank=True, null=True, verbose_name='Телефон')
    logo_url = models.URLField(blank=True, null=True, verbose_name='Логотип компании')

    # Donation details
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(1)], verbose_name='Сумма')
    is_anonymous = models.BooleanField(default=False, verbose_name='Анонимное пожертвование')
    tier = models.CharField(max_length=20, choices=TIER_CHOICES, default='none', verbose_name='Уровень партнерства')

    # Additional info
    message = models.TextField(blank=True, null=True, verbose_name='Сообщение')

    # Payment info
    payment_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Ожидает оплаты'),
            ('paid', 'Оплачено'),
            ('failed', 'Ошибка'),
        ],
        default='pending',
        verbose_name='Статус оплаты'
    )
    payment_date = models.DateTimeField(blank=True, null=True, verbose_name='Дата оплаты')
    transaction_id = models.CharField(max_length=100, unique=True, verbose_name='ID транзакции')

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    # Show on leaderboard
    show_on_leaderboard = models.BooleanField(default=True, verbose_name='Показывать в лидерборде')

    class Meta:
        db_table = 'donations'
        verbose_name = 'Пожертвование'
        verbose_name_plural = 'Пожертвования'
        ordering = ['-created_at']

    def __str__(self):
        if self.is_anonymous:
            return f'Анонимное пожертвование - {self.amount} руб.'
        return f'{self.get_donor_display_name()} - {self.amount} руб.'

    def get_donor_display_name(self):
        """Get display name for leaderboard"""
        if self.is_anonymous:
            return 'Анонимный донор'
        if self.donor_type == 'company' and self.company_name:
            return self.company_name
        if self.donor_name:
            return self.donor_name
        return 'Благотворитель'

    def calculate_tier(self):
        """Calculate partnership tier based on amount"""
        if self.amount >= 100000:
            return 'gold'
        elif self.amount >= 50000:
            return 'silver'
        elif self.amount >= 25000:
            return 'bronze'
        return 'none'

    def save(self, *args, **kwargs):
        # Auto-calculate tier for company donations
        if self.donor_type in ['company', 'ip']:
            self.tier = self.calculate_tier()
        super().save(*args, **kwargs)
