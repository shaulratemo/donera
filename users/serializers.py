from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import UserProfile
from causes.models import Category

# This dynamically retrieves the custom user model
User = get_user_model()

class UserProfileSerializer(serializers.ModelSerializer):
    interests = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Category.objects.all(),
        required=False,
    )

    class Meta:
        model = UserProfile
        fields = ["interests", "is_onboarded"]
        read_only_fields = ["is_onboarded"]

    def validate_interests(self, value):
        if value is not None and len(value) < 3:
            raise serializers.ValidationError("Please select at least 3 interests.")
        return value

    def update(self, instance, validated_data):
        interests = validated_data.pop("interests", None)

        if interests is not None:
            instance.interests.set(interests)
            instance.is_onboarded = True

            instance.save(update_fields=["is_onboarded", "updated_at"])
        return instance

class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()
    
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "full_name",
            "role",
            "phone_number",
            "created_at",
            "updated_at",
        ]
        # This protects the fields that should never be altered via an API request
        read_only_fields = ["id", "role", "created_at", "updated_at"]

class UserRegistrationSerializer(serializers.ModelSerializer):
    # Define the password field to be write_only
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    interests = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        many=True,
        required=False,
        write_only=True,
        help_text="List of category IDs representing user interests"
    )
    
    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password",
            "first_name",
            "last_name",
            "role",
            "phone_number",
            "interests"
        ]
        read_only_fields = []

    def validate_interests(self, value):
        if value is not None and len(value) < 3:
            raise serializers.ValidationError("Please select at least 3 interests.")
        return value
    
    # Intercepting the saving process to hash the password
    def create(self, validated_data):
        # Extract interests before user creation to avoid passing non-user fields.
        password = validated_data.pop('password')
        interests_missing = object()
        interests = validated_data.pop('interests', interests_missing)

        user = User.objects.create_user(password=password, **validated_data)

        # If interests field is provided and validated, persist it and mark onboarding complete.
        if interests is not interests_missing:
            user.profile.interests.set(interests)
            user.profile.is_onboarded = True
            user.profile.save(update_fields=["is_onboarded", "updated_at"])
        
        return user

class MiniUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "full_name"
        ]
        
        read_only_fields = ["id"]


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @staticmethod
    def _has_organization(user):
        try:
            return user.organization is not None
        except ObjectDoesNotExist:
            return False

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["role"] = user.role
        token["has_organization"] = cls._has_organization(user)
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data["role"] = self.user.role
        data["has_organization"] = self._has_organization(self.user)
        return data