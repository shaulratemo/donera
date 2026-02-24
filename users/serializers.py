from rest_framework import serializers
from django.contrib.auth import get_user_model

# This dynamically retrieves the custom user model
User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()
    
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "full_name",
            "role",
            "phone_number",
            "created_at",
            "updated_at",
        ]
        # This protects the fields that should never be altered via an API request
        read_only_fields = ["id", "created_at", "updated_at"]

class UserRegistrationSerializer(serializers.ModelSerializer):
    # Define the password field to be write_only
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
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
            "phone_number"
        ]
    
    # Intercepting the saving process to hash the password
    def create(self, validated_data):
        # Extract the password from the validated data
        password = validated_data.pop('password')
        
        user = User(**validated_data)
        # Hashing the password and attaching it to the user
        user.set_password(password)
        user.save()
        
        return user

class MiniUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "full_name"
        ]
        
        read_only_fields = ["id"]