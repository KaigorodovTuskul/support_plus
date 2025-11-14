from rest_framework import serializers
from users.models import User, UserProfile, VerificationRequest
from benefits.models import Benefit, CommercialOffer, Category, Region, UserBenefitInteraction


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = [
            'font_size', 'font_family', 'letter_spacing', 'color_mode',
            'show_images', 'speech_assistant_enabled', 'interest_categories',
            'hidden_benefits'
        ]


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)
    masked_snils = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'phone', 'beneficiary_category',
            'region', 'masked_snils', 'is_verified', 'verification_date',
            'created_at', 'profile'
        ]
        read_only_fields = ['id', 'is_verified', 'verification_date', 'created_at']

    def get_masked_snils(self, obj):
        return obj.get_masked_snils()


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'}, label='Confirm password')

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2', 'phone', 'beneficiary_category', 'region', 'snils']

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Пароли не совпадают"})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')
        user = User.objects.create_user(password=password, **validated_data)

        # Create user profile
        UserProfile.objects.create(user=user)

        return user


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'icon']


class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ['id', 'code', 'name']


class BenefitSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True, read_only=True)
    regions = RegionSerializer(many=True, read_only=True)
    is_relevant = serializers.SerializerMethodField()

    class Meta:
        model = Benefit
        fields = [
            'id', 'benefit_id', 'title', 'description', 'benefit_type',
            'target_groups', 'regions', 'applies_to_all_regions',
            'valid_from', 'valid_to', 'status', 'requirements',
            'how_to_get', 'documents_needed', 'source_url',
            'categories', 'views_count', 'popularity_score',
            'created_at', 'is_relevant'
        ]

    def get_is_relevant(self, obj):
        """Check if benefit is relevant to current user"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            user = request.user
            # Check if user's category is in target groups
            if user.beneficiary_category in obj.target_groups:
                return True
        return False


class BenefitDetailSerializer(BenefitSerializer):
    """More detailed serializer for individual benefit view"""
    pass


class CommercialOfferSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True, read_only=True)
    regions = RegionSerializer(many=True, read_only=True)
    is_relevant = serializers.SerializerMethodField()

    class Meta:
        model = CommercialOffer
        fields = [
            'id', 'offer_id', 'title', 'description', 'discount_percentage',
            'discount_description', 'partner_name', 'partner_logo',
            'partner_website', 'partner_category', 'target_groups',
            'regions', 'applies_to_all_regions', 'locations',
            'valid_from', 'valid_to', 'status', 'how_to_use',
            'promo_code', 'categories', 'views_count', 'popularity_score',
            'created_at', 'is_relevant'
        ]

    def get_is_relevant(self, obj):
        """Check if offer is relevant to current user"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            user = request.user
            if user.beneficiary_category in obj.target_groups:
                return True
        return False


class UserBenefitInteractionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserBenefitInteraction
        fields = ['id', 'benefit', 'offer', 'interaction_type', 'created_at']
        read_only_fields = ['id', 'created_at']


class VerificationRequestSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = VerificationRequest
        fields = ['id', 'user', 'status', 'documents', 'notes', 'created_at', 'reviewed_at']
        read_only_fields = ['id', 'created_at', 'reviewed_at']
