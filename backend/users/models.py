from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator


class User(AbstractUser):
    """Extended user model with beneficiary information"""

    BENEFICIARY_CATEGORIES = [
        ('pensioner', 'Пенсионер'),
        ('disability_1', 'Инвалидность 1 группы'),
        ('disability_2', 'Инвалидность 2 группы'),
        ('disability_3', 'Инвалидность 3 группы'),
        ('large_family', 'Многодетная семья'),
        ('veteran', 'Ветеран'),
        ('low_income', 'Малоимущий'),
        ('svo_participant', 'Участник СВО'),
        ('svo_family', 'Семья участника СВО'),
    ]

    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    beneficiary_category = models.CharField(
        max_length=20,
        choices=BENEFICIARY_CATEGORIES,
        blank=True,
        null=True
    )
    region = models.CharField(max_length=100, help_text='Регион проживания')

    # SNILS number (masked for privacy)
    snils_validator = RegexValidator(
        regex=r'^\d{3}-\d{3}-\d{3} \d{2}$',
        message='СНИЛС должен быть в формате XXX-XXX-XXX XX'
    )
    snils = models.CharField(
        max_length=14,
        validators=[snils_validator],
        blank=True,
        null=True,
        help_text='Индивидуальный номер страхового счета (СНИЛС)'
    )

    is_verified = models.BooleanField(default=False, help_text='Статус верификации льготника')
    verification_date = models.DateTimeField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_masked_snils(self):
        """Return masked SNILS for privacy (XXX-XXX-***-**)"""
        if not self.snils:
            return None
        parts = self.snils.split('-')
        if len(parts) == 3:
            return f"{parts[0]}-{parts[1]}-***-**"
        return "***-***-***-**"

    def __str__(self):
        return f"{self.username} ({self.email})"

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class UserProfile(models.Model):
    """User preferences and additional profile information"""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')

    # Accessibility preferences
    font_size = models.CharField(
        max_length=10,
        choices=[('normal', 'Обычный'), ('enlarged', 'Увеличенный'), ('huge', 'Огромный')],
        default='normal'
    )
    font_family = models.CharField(
        max_length=10,
        choices=[('sans-serif', 'Без засечек'), ('serif', 'С засечками')],
        default='sans-serif'
    )
    letter_spacing = models.CharField(
        max_length=10,
        choices=[('normal', 'Обычный'), ('enlarged', 'Увеличенный'), ('huge', 'Огромный')],
        default='normal'
    )
    color_mode = models.CharField(
        max_length=20,
        choices=[
            ('default', 'По умолчанию'),
            ('monochrome', 'Монохромный'),
            ('inverted', 'Инверсия'),
            ('blue_bg', 'Синий фон')
        ],
        default='default'
    )
    show_images = models.BooleanField(default=True)
    speech_assistant_enabled = models.BooleanField(default=False)

    # Interest categories
    interest_categories = models.JSONField(default=list, blank=True)

    # Hidden benefits (user doesn't want to see them)
    hidden_benefits = models.JSONField(default=list, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile of {self.user.username}"

    class Meta:
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'


class VerificationRequest(models.Model):
    """Track beneficiary verification requests"""

    STATUS_CHOICES = [
        ('pending', 'Ожидает проверки'),
        ('approved', 'Одобрено'),
        ('rejected', 'Отклонено'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='verification_requests')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    documents = models.JSONField(default=dict, help_text='Загруженные документы')
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    reviewed_at = models.DateTimeField(blank=True, null=True)
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_verifications'
    )

    def __str__(self):
        return f"Verification for {self.user.username} - {self.status}"

    class Meta:
        verbose_name = 'Запрос на верификацию'
        verbose_name_plural = 'Запросы на верификацию'
        ordering = ['-created_at']
