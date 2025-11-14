from django.db import models
from django.core.validators import URLValidator


class Category(models.Model):
    """Category for organizing benefits"""

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text='Icon name for UI')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['name']


class Region(models.Model):
    """Russian regions"""

    code = models.CharField(max_length=2, unique=True, help_text='Код региона')
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return f"{self.name} ({self.code})"

    class Meta:
        verbose_name = 'Регион'
        verbose_name_plural = 'Регионы'
        ordering = ['name']


class Benefit(models.Model):
    """Government benefit or entitlement"""

    TYPE_CHOICES = [
        ('federal', 'Федеральная'),
        ('regional', 'Региональная'),
        ('municipal', 'Муниципальная'),
    ]

    STATUS_CHOICES = [
        ('active', 'Активна'),
        ('expiring_soon', 'Скоро истекает'),
        ('expired', 'Истекла'),
        ('requires_verification', 'Требует верификации'),
    ]

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

    # Basic information
    benefit_id = models.CharField(max_length=100, unique=True, help_text='Уникальный идентификатор')
    title = models.CharField(max_length=255)
    description = models.TextField()
    benefit_type = models.CharField(max_length=20, choices=TYPE_CHOICES)

    # Target audience
    target_groups = models.JSONField(
        default=list,
        help_text='Список категорий льготников, например: ["pensioner", "disabled"]'
    )

    # Geographic coverage
    regions = models.ManyToManyField(Region, blank=True, related_name='benefits')
    applies_to_all_regions = models.BooleanField(default=False)

    # Validity
    valid_from = models.DateField()
    valid_to = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default='active')

    # Requirements and instructions
    requirements = models.TextField(help_text='Что нужно для получения')
    how_to_get = models.TextField(help_text='Как получить эту льготу')
    documents_needed = models.JSONField(default=list, blank=True)

    # Source and verification
    source_url = models.URLField(validators=[URLValidator()], help_text='Источник информации')
    last_verified = models.DateTimeField(auto_now=True)

    # Categories
    categories = models.ManyToManyField(Category, related_name='benefits', blank=True)

    # Metadata
    views_count = models.IntegerField(default=0)
    popularity_score = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.benefit_type})"

    class Meta:
        verbose_name = 'Льгота'
        verbose_name_plural = 'Льготы'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['benefit_type', 'status']),
            models.Index(fields=['valid_from', 'valid_to']),
        ]


class CommercialOffer(models.Model):
    """Commercial discounts and offers from partners"""

    STATUS_CHOICES = [
        ('active', 'Активно'),
        ('expiring_soon', 'Скоро истекает'),
        ('expired', 'Истекло'),
    ]

    # Basic information
    offer_id = models.CharField(max_length=100, unique=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    discount_description = models.CharField(max_length=255, help_text='Например: "Скидка 15%" или "2 по цене 1"')

    # Partner information
    partner_name = models.CharField(max_length=255)
    partner_logo = models.ImageField(upload_to='partners/', blank=True, null=True)
    partner_website = models.URLField(blank=True)
    partner_category = models.CharField(max_length=100, help_text='Аптека, Магазин, Услуги и т.д.')

    # Target audience
    target_groups = models.JSONField(
        default=list,
        help_text='Список категорий льготников'
    )

    # Geographic coverage
    regions = models.ManyToManyField(Region, blank=True, related_name='offers')
    applies_to_all_regions = models.BooleanField(default=False)
    locations = models.JSONField(default=list, blank=True, help_text='Адреса точек продаж')

    # Validity
    valid_from = models.DateField()
    valid_to = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')

    # How to use
    how_to_use = models.TextField(help_text='Как воспользоваться предложением')
    promo_code = models.CharField(max_length=50, blank=True, help_text='Промокод если есть')

    # Categories
    categories = models.ManyToManyField(Category, related_name='offers', blank=True)

    # Metadata
    views_count = models.IntegerField(default=0)
    popularity_score = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.partner_name}"

    class Meta:
        verbose_name = 'Коммерческое предложение'
        verbose_name_plural = 'Коммерческие предложения'
        ordering = ['-created_at']


class UserBenefitInteraction(models.Model):
    """Track user interactions with benefits and offers"""

    INTERACTION_TYPES = [
        ('view', 'Просмотр'),
        ('save', 'Сохранение'),
        ('hide', 'Скрытие'),
        ('export', 'Экспорт'),
    ]

    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='benefit_interactions')
    benefit = models.ForeignKey(Benefit, on_delete=models.CASCADE, null=True, blank=True, related_name='interactions')
    offer = models.ForeignKey(CommercialOffer, on_delete=models.CASCADE, null=True, blank=True, related_name='interactions')
    interaction_type = models.CharField(max_length=10, choices=INTERACTION_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        item = self.benefit or self.offer
        return f"{self.user.username} - {self.interaction_type} - {item}"

    class Meta:
        verbose_name = 'Взаимодействие пользователя'
        verbose_name_plural = 'Взаимодействия пользователей'
        ordering = ['-created_at']
