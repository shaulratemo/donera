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
            "kra_pin",
            "tcc_number",
            "tcc_document",
            "verification_status",
            "payout_method",
            "payout_bank_name",
            "payout_shortcode",
            "payout_account_number",
            "verified_at",
            "contact_email",
            "contact_phone",
            "physical_address",
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