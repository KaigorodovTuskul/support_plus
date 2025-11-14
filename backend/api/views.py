from rest_framework import viewsets, status, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
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
    VerificationRequestSerializer
)


@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """Register a new user"""
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()

        # Generate tokens
        refresh = RefreshToken.for_user(user)

        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
                queryset = queryset.filter(target_groups__contains=[user.beneficiary_category])

        # Exclude hidden benefits
        if hasattr(user, 'profile'):
            hidden = user.profile.hidden_benefits
            if hidden:
                queryset = queryset.exclude(id__in=hidden)

        return queryset

    def retrieve(self, request, *args, **kwargs):
        """Track view when benefit is retrieved"""
        instance = self.get_object()
        instance.views_count += 1
        instance.save(update_fields=['views_count'])

        # Log interaction
        UserBenefitInteraction.objects.create(
            user=request.user,
            benefit=instance,
            interaction_type='view'
        )

        return super().retrieve(request, *args, **kwargs)

    @action(detail=False, methods=['get'])
    def recommended(self, request):
        """Get personalized recommended benefits"""
        user = request.user

        # Filter by user's beneficiary category and region
        queryset = self.get_queryset()

        if user.beneficiary_category:
            queryset = queryset.filter(target_groups__contains=[user.beneficiary_category])

        if user.region:
            queryset = queryset.filter(
                Q(applies_to_all_regions=True) | Q(regions__name__icontains=user.region)
            )

        # Prioritize by status and popularity
        queryset = queryset.filter(status='active').order_by('-popularity_score', '-created_at')[:10]

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Get dashboard data for user"""
        user = request.user
        queryset = self.get_queryset()

        # Get active benefits for user
        active = queryset.filter(status='active')
        if user.beneficiary_category:
            active = active.filter(target_groups__contains=[user.beneficiary_category])

        # Get expiring soon
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
                queryset = queryset.filter(target_groups__contains=[user.beneficiary_category])

        return queryset

    def retrieve(self, request, *args, **kwargs):
        """Track view when offer is retrieved"""
        instance = self.get_object()
        instance.views_count += 1
        instance.save(update_fields=['views_count'])

        # Log interaction
        UserBenefitInteraction.objects.create(
            user=request.user,
            offer=instance,
            interaction_type='view'
        )

        return super().retrieve(request, *args, **kwargs)


class UserProfileViewSet(viewsets.ModelViewSet):
    """ViewSet for user profile"""
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserProfile.objects.filter(user=self.request.user)

    def get_object(self):
        return self.request.user.profile

    @action(detail=False, methods=['post'])
    def hide_benefit(self, request):
        """Hide a benefit from user's view"""
        profile = request.user.profile
        benefit_id = request.data.get('benefit_id')

        if benefit_id and benefit_id not in profile.hidden_benefits:
            profile.hidden_benefits.append(benefit_id)
            profile.save()

        return Response({'status': 'benefit hidden'})

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


class RegionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for regions"""
    queryset = Region.objects.all()
    serializer_class = RegionSerializer
    permission_classes = [IsAuthenticated]


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
    benefits = Benefit.objects.filter(
        target_groups__contains=[user.beneficiary_category]
    )[:10]

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


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_info(request):
    """Get current user information"""
    serializer = UserSerializer(request.user)
    return Response(serializer.data)
