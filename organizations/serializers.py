from rest_framework import serializers
from .models import Organization
from users.serializers import UserSerializer

class OrganizationSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    
    class Meta:
        model = Organization
        fields = [
            "id",
            "owner",
            "name",
            "description",
            "registration_number",
            "verification_status",
            "verified_at",
            "contact_email",
            "contact_phone",
            "created_at",
            "updated_at"
        ]
        
        read_only_fields = ["id", "verification_status", "verified_at", "created_at", "updated_at"]

class MiniOrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = [
            "id",
            "name"
        ]
        
        read_only_fields = ["id"]