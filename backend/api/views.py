from rest_framework import viewsets, status, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from django.http import HttpResponse

from users.models import User, UserProfile, VerificationRequest
from benefits.models import Benefit, CommercialOffer, Category, Region, UserBenefitInteraction
from .serializers import (
    UserSerializer, UserProfileSerializer, UserRegistrationSerializer,
    BenefitSerializer, BenefitDetailSerializer, CommercialOfferSerializer,
    CategorySerializer, RegionSerializer, UserBenefitInteractionSerializer,
    VerificationRequestSerializer, CustomTokenObtainPairSerializer
)

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# Reusable schemas
paginated_response = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'count': openapi.Schema(type=openapi.TYPE_INTEGER),
        'next': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_URI, nullable=True),
        'previous': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_URI, nullable=True),
        'results': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_OBJECT)),
    }
)

error_response = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'message': openapi.Schema(type=openapi.TYPE_STRING),
        'error': openapi.Schema(type=openapi.TYPE_STRING, nullable=True),
    }
)


def filter_by_target_groups(queryset, category):
    """
    Filter queryset by target group category.
    Works with SQLite by filtering in Python instead of using JSONField __contains.
    Works for both Benefits and CommercialOffers.
    """
    if not category:
        return queryset

    # Get all items and filter in Python
    all_items = list(queryset)
    filtered_ids = [
        item.id for item in all_items
        if item.target_groups and category in item.target_groups
    ]
    return queryset.filter(id__in=filtered_ids) if filtered_ids else queryset.none()


@swagger_auto_schema(
    method='post',
    operation_summary='Регистрация нового пользователя',
    operation_description='Создает нового пользователя и возвращает JWT токены доступа',
    request_body=UserRegistrationSerializer,
    responses={
        201: openapi.Response(
            description='Успешная регистрация',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'user': openapi.Schema(type=openapi.TYPE_OBJECT, description='Данные пользователя'),
                    'tokens': openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'refresh': openapi.Schema(type=openapi.TYPE_STRING, description='Refresh token'),
                            'access': openapi.Schema(type=openapi.TYPE_STRING, description='Access token'),
                        }
                    )
                }
            )
        ),
        400: openapi.Response(description='Ошибка валидации', schema=error_response),
    },
    tags=['Авторизация']
)
@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """Register a new user"""
    # Debug logging
    print("=== REGISTRATION DEBUG ===")
    print("Request data:", request.data)
    print("Password received:", request.data.get('password'))
    print("Password2 received:", request.data.get('password2'))

    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()

        # Verify password was set correctly
        print(f"User created: {user.username}")
        print(f"Password check after creation: {user.check_password(request.data.get('password'))}")

        # Generate tokens
        refresh = RefreshToken.for_user(user)

        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)

    print("Serializer errors:", serializer.errors)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='post',
    operation_summary='Mock OAuth вход через Госуслуги',
    operation_description='Заглушка для OAuth авторизации через портал Госуслуги',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'email': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL, description='Email пользователя'),
            'beneficiary_category': openapi.Schema(type=openapi.TYPE_STRING, enum=['pensioner', 'disabled', 'large_family'], description='Категория льготника'),
            'region': openapi.Schema(type=openapi.TYPE_STRING, description='Регион пользователя'),
        },
        required=['email']
    ),
    responses={
        200: openapi.Response(
            description='Успешный вход',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'user': openapi.Schema(type=openapi.TYPE_OBJECT, description='Данные пользователя'),
                    'tokens': openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'refresh': openapi.Schema(type=openapi.TYPE_STRING),
                            'access': openapi.Schema(type=openapi.TYPE_STRING),
                        }
                    )
                }
            )
        ),
        400: openapi.Response(description='Email required', schema=error_response),
    },
    tags=['Авторизация']
)
@api_view(['POST'])
@permission_classes([AllowAny])
def mock_oauth_login(request):
    """Mock Gosuslugi OAuth login"""
    # This is a simplified mock - in production, you'd implement proper OAuth flow
    email = request.data.get('email')

    if not email:
        return Response({'error': 'Email required'}, status=status.HTTP_400_BAD_REQUEST)

    # Try to find existing user or create new one
    user, created = User.objects.get_or_create(
        email=email,
        defaults={
            'username': email.split('@')[0],
            'beneficiary_category': request.data.get('beneficiary_category', 'pensioner'),
            'region': request.data.get('region', 'Москва'),
        }
    )

    if created:
        UserProfile.objects.create(user=user)

    # Generate tokens
    refresh = RefreshToken.for_user(user)

    return Response({
        'user': UserSerializer(user).data,
        'tokens': {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
    })


class BenefitViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for benefits"""
    queryset = Benefit.objects.all().prefetch_related('categories', 'regions')
    serializer_class = BenefitSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'requirements']
    ordering_fields = ['created_at', 'popularity_score', 'valid_from']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return BenefitDetailSerializer
        return BenefitSerializer

    @swagger_auto_schema(
        operation_summary='Получить список льгот',
        operation_description='Возвращает список льгот с возможностью фильтрации, поиска и сортировки',
        manual_parameters=[
            openapi.Parameter('type', openapi.IN_QUERY, description='Тип льготы (federal/regional/municipal)', type=openapi.TYPE_STRING, enum=['federal', 'regional', 'municipal']),
            openapi.Parameter('status', openapi.IN_QUERY, description='Статус льготы', type=openapi.TYPE_STRING, enum=['active', 'expiring_soon', 'expired']),
            openapi.Parameter('region', openapi.IN_QUERY, description='Название региона', type=openapi.TYPE_STRING),
            openapi.Parameter('category', openapi.IN_QUERY, description='Slug категории', type=openapi.TYPE_STRING),
            openapi.Parameter('personalized', openapi.IN_QUERY, description='Персонализировать по категории пользователя', type=openapi.TYPE_BOOLEAN),
            openapi.Parameter('search', openapi.IN_QUERY, description='Поиск по тексту', type=openapi.TYPE_STRING),
            openapi.Parameter('ordering', openapi.IN_QUERY, description='Сортировка', type=openapi.TYPE_STRING, enum=['created_at', '-created_at', 'popularity_score', '-popularity_score', 'valid_from', '-valid_from']),
            openapi.Parameter('page', openapi.IN_QUERY, description='Номер страницы', type=openapi.TYPE_INTEGER),
        ],
        responses={
            200: openapi.Response('Список льгот', paginated_response),
            401: openapi.Response('Не авторизован'),
        },
        tags=['Льготы']
    )
    def list(self, request, *args, **kwargs):
        """List benefits with filtering"""
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary='Получить детали льготы',
        operation_description='Возвращает полную информацию о конкретной льготе',
        responses={
            200: openapi.Response('Детали льготы', schema=openapi.Schema(type=openapi.TYPE_OBJECT)),
            404: openapi.Response('Льгота не найдена'),
            401: openapi.Response('Не авторизован'),
        },
        tags=['Льготы']
    )
    def retrieve(self, request, *args, **kwargs):
        """Track view when benefit is retrieved"""
        instance = self.get_object()
        instance.views_count += 1
        instance.save(update_fields=['views_count'])

        UserBenefitInteraction.objects.create(
            user=request.user,
            benefit=instance,
            interaction_type='view'
        )

        return super().retrieve(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        # Filter by type
        benefit_type = self.request.query_params.get('type')
        if benefit_type:
            queryset = queryset.filter(benefit_type=benefit_type)

        # Filter by status
        benefit_status = self.request.query_params.get('status')
        if benefit_status:
            queryset = queryset.filter(status=benefit_status)

        # Filter by region
        region = self.request.query_params.get('region')
        if region:
            queryset = queryset.filter(
                Q(applies_to_all_regions=True) | Q(regions__name__icontains=region)
            ).distinct()

        # Filter by category
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(categories__slug=category)

        # Filter by target group (personalized)
        if self.request.query_params.get('personalized') == 'true':
            if user.beneficiary_category:
                queryset = filter_by_target_groups(queryset, user.beneficiary_category)

        # Exclude hidden benefits
        if hasattr(user, 'profile'):
            hidden = user.profile.hidden_benefits
            if hidden:
                queryset = queryset.exclude(id__in=hidden)

        return queryset

    @swagger_auto_schema(
        operation_summary='Получить персонализированные рекомендации',
        operation_description='Возвращает список льгот, рекомендованных для текущего пользователя',
        responses={
            200: openapi.Response('Список рекомендованных льгот', paginated_response),
            401: openapi.Response('Не авторизован'),
        },
        tags=['Льготы']
    )
    @action(detail=False, methods=['get'])
    def recommended(self, request):
        """Get personalized recommended benefits"""
        user = request.user
        queryset = self.get_queryset()

        if user.beneficiary_category:
            queryset = filter_by_target_groups(queryset, user.beneficiary_category)

        if user.region:
            queryset = queryset.filter(
                Q(applies_to_all_regions=True) | Q(regions__name__icontains=user.region)
            )

        queryset = queryset.filter(status='active').order_by('-popularity_score', '-created_at')[:10]

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary='Получить данные дашборда',
        operation_description='Возвращает статистику и список активных/истекающих льгот для пользователя',
        responses={
            200: openapi.Response(
                'Данные дашборда',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'active_count': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'expiring_count': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'active_benefits': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_OBJECT)),
                        'expiring_benefits': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_OBJECT)),
                    }
                )
            ),
            401: openapi.Response('Не авторизован'),
        },
        tags=['Льготы']
    )
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Get dashboard data for user"""
        user = request.user
        queryset = self.get_queryset()

        active = queryset.filter(status='active')
        if user.beneficiary_category:
            active = filter_by_target_groups(active, user.beneficiary_category)

        expiring_date = timezone.now().date() + timedelta(days=30)
        expiring = active.filter(valid_to__lte=expiring_date, valid_to__gte=timezone.now().date())

        return Response({
            'active_count': active.count(),
            'expiring_count': expiring.count(),
            'active_benefits': BenefitSerializer(active[:5], many=True, context={'request': request}).data,
            'expiring_benefits': BenefitSerializer(expiring, many=True, context={'request': request}).data,
        })


class CommercialOfferViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for commercial offers"""
    queryset = CommercialOffer.objects.all().prefetch_related('categories', 'regions')
    serializer_class = CommercialOfferSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'partner_name']
    ordering_fields = ['created_at', 'popularity_score', 'valid_from']
    ordering = ['-created_at']

    @swagger_auto_schema(
        operation_summary='Получить список коммерческих предложений',
        operation_description='Возвращает список предложений от партнеров',
        manual_parameters=[
            openapi.Parameter('partner_category', openapi.IN_QUERY, description='Категория партнера', type=openapi.TYPE_STRING),
            openapi.Parameter('region', openapi.IN_QUERY, description='Регион', type=openapi.TYPE_STRING),
            openapi.Parameter('personalized', openapi.IN_QUERY, description='Персонализировать по пользователю', type=openapi.TYPE_BOOLEAN),
            openapi.Parameter('search', openapi.IN_QUERY, description='Поиск по тексту', type=openapi.TYPE_STRING),
            openapi.Parameter('ordering', openapi.IN_QUERY, description='Сортировка', type=openapi.TYPE_STRING),
        ],
        responses={200: openapi.Response('Список коммерческих предложений', paginated_response)},
        tags=['Коммерческие предложения']
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary='Получить детали коммерческого предложения',
        responses={
            200: openapi.Response('Детали предложения'),
            404: openapi.Response('Предложение не найдено'),
            401: openapi.Response('Не авторизован'),
        },
        tags=['Коммерческие предложения']
    )
    def retrieve(self, request, *args, **kwargs):
        """Track view when offer is retrieved"""
        instance = self.get_object()
        instance.views_count += 1
        instance.save(update_fields=['views_count'])

        UserBenefitInteraction.objects.create(
            user=request.user,
            offer=instance,
            interaction_type='view'
        )

        return super().retrieve(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        # Filter by partner category
        partner_category = self.request.query_params.get('partner_category')
        if partner_category:
            queryset = queryset.filter(partner_category__icontains=partner_category)

        # Filter by region
        region = self.request.query_params.get('region')
        if region:
            queryset = queryset.filter(
                Q(applies_to_all_regions=True) | Q(regions__name__icontains=region)
            ).distinct()

        # Personalized
        if self.request.query_params.get('personalized') == 'true':
            if user.beneficiary_category:
                queryset = filter_by_target_groups(queryset, user.beneficiary_category)

        return queryset


class UserProfileViewSet(viewsets.ModelViewSet):
    """ViewSet for user profile"""
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary='Получить профиль пользователя',
        responses={200: openapi.Response('Данные профиля', UserProfileSerializer)},
        tags=['Профиль пользователя']
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary='Обновить профиль пользователя',
        request_body=UserProfileSerializer,
        responses={
            200: openapi.Response('Обновленные данные', UserProfileSerializer),
            400: openapi.Response('Ошибка валидации', error_response),
        },
        tags=['Профиль пользователя']
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return UserProfile.objects.none()
        return UserProfile.objects.filter(user=self.request.user)

    def get_object(self):
        return self.request.user.profile

    @swagger_auto_schema(
        operation_summary='Скрыть льготу',
        operation_description='Добавляет льготу в список скрытых для пользователя',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'benefit_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID льготы'),
            },
            required=['benefit_id']
        ),
        responses={
            200: openapi.Response('Льгота скрыта', schema=openapi.Schema(type=openapi.TYPE_OBJECT, properties={'status': openapi.Schema(type=openapi.TYPE_STRING)})),
            400: openapi.Response('Ошибка', error_response),
        },
        tags=['Профиль пользователя']
    )
    @action(detail=False, methods=['post'])
    def hide_benefit(self, request):
        """Hide a benefit from user's view"""
        profile = request.user.profile
        benefit_id = request.data.get('benefit_id')

        if benefit_id and benefit_id not in profile.hidden_benefits:
            profile.hidden_benefits.append(benefit_id)
            profile.save()

        return Response({'status': 'benefit hidden'})

    @swagger_auto_schema(
        operation_summary='Показать льготу',
        operation_description='Убирает льготу из списка скрытых',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'benefit_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID льготы'),
            },
            required=['benefit_id']
        ),
        responses={
            200: openapi.Response('Льгота показана', schema=openapi.Schema(type=openapi.TYPE_OBJECT, properties={'status': openapi.Schema(type=openapi.TYPE_STRING)})),
            400: openapi.Response('Ошибка', error_response),
        },
        tags=['Профиль пользователя']
    )
    @action(detail=False, methods=['post'])
    def unhide_benefit(self, request):
        """Unhide a benefit"""
        profile = request.user.profile
        benefit_id = request.data.get('benefit_id')

        if benefit_id and benefit_id in profile.hidden_benefits:
            profile.hidden_benefits.remove(benefit_id)
            profile.save()

        return Response({'status': 'benefit unhidden'})


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for categories"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary='Получить список категорий',
        responses={200: openapi.Response('Список категорий', paginated_response)},
        tags=['Справочники']
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary='Получить детали категории',
        responses={200: openapi.Response('Детали категории'), 404: openapi.Response('Категория не найдена')},
        tags=['Справочники']
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


class RegionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for regions"""
    queryset = Region.objects.all()
    serializer_class = RegionSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary='Получить список регионов',
        responses={200: openapi.Response('Список регионов', paginated_response)},
        tags=['Справочники']
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary='Получить детали региона',
        responses={200: openapi.Response('Детали региона'), 404: openapi.Response('Регион не найден')},
        tags=['Справочники']
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


@swagger_auto_schema(
    method='get',
    operation_summary='Экспорт льгот в PDF',
    operation_description='Генерирует PDF-файл со списком доступных пользователю льгот',
    responses={
        200: openapi.Response(
            description='PDF файл',
            content={'application/pdf': {}}
        ),
        401: openapi.Response('Не авторизован'),
    },
    tags=['Экспорт']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_benefits_pdf(request):
    """Export user's benefits to PDF"""
    user = request.user

    # Create PDF
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)

    # Add content
    p.drawString(100, 750, f"Мои льготы - {user.username}")
    p.drawString(100, 730, f"Категория: {user.get_beneficiary_category_display()}")
    p.drawString(100, 710, f"Регион: {user.region}")

    # Get user's benefits
    all_benefits = Benefit.objects.all()
    benefits = filter_by_target_groups(all_benefits, user.beneficiary_category)[:10]

    y = 680
    for benefit in benefits:
        p.drawString(100, y, f"• {benefit.title}")
        y -= 20
        if y < 100:
            break

    p.showPage()
    p.save()

    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="my_benefits.pdf"'

    return response


@swagger_auto_schema(
    method='get',
    operation_summary='Получить информацию о текущем пользователе',
    responses={
        200: openapi.Response('Данные пользователя', UserSerializer),
        401: openapi.Response('Не авторизован'),
    },
    tags=['Пользователь']
)
@swagger_auto_schema(
    method='patch',
    operation_summary='Обновить информацию о пользователе',
    request_body=openapi.Schema(type=openapi.TYPE_OBJECT, description='Поля для обновления'),
    responses={
        200: openapi.Response('Обновленные данные', UserSerializer),
        400: openapi.Response('Ошибка валидации', error_response),
        401: openapi.Response('Не авторизован'),
    },
    tags=['Пользователь']
)
@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def user_info(request):
    """Get or update current user information"""
    if request.method == 'GET':
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    elif request.method == 'PATCH':
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='post',
    operation_summary='Смена пароля пользователя',
    operation_description='Изменяет пароль текущего пользователя после проверки текущего пароля',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['current_password', 'new_password'],
        properties={
            'current_password': openapi.Schema(type=openapi.TYPE_STRING, description='Текущий пароль'),
            'new_password': openapi.Schema(type=openapi.TYPE_STRING, description='Новый пароль'),
        }
    ),
    responses={
        200: openapi.Response('Пароль успешно изменен', schema=openapi.Schema(type=openapi.TYPE_OBJECT, properties={'message': openapi.Schema(type=openapi.TYPE_STRING)})),
        400: openapi.Response('Ошибка валидации', error_response),
        401: openapi.Response('Не авторизован'),
    },
    tags=['Пользователь']
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """Change user password"""
    user = request.user
    current_password = request.data.get('current_password')
    new_password = request.data.get('new_password')

    if not current_password or not new_password:
        return Response({'message': 'Необходимо указать текущий и новый пароль'}, status=status.HTTP_400_BAD_REQUEST)

    if not user.check_password(current_password):
        return Response({'message': 'Неверный текущий пароль'}, status=status.HTTP_400_BAD_REQUEST)

    user.set_password(new_password)
    user.save()

    return Response({'message': 'Пароль успешно изменен'})


class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom token view that uses email for authentication"""

    @swagger_auto_schema(
        operation_summary='Получить JWT токен',
        operation_description='Аутентификация по email и паролю. Возвращает JWT токены доступа и обновления.',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email', 'password'],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL, description='Email пользователя'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='Пароль'),
            }
        ),
        responses={
            200: openapi.Response(
                description='Токены успешно созданы',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'refresh': openapi.Schema(type=openapi.TYPE_STRING, description='Refresh token'),
                        'access': openapi.Schema(type=openapi.TYPE_STRING, description='Access token'),
                    }
                )
            ),
            401: openapi.Response(description='Неверные учетные данные', schema=error_response),
        },
        tags=['Авторизация']
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)