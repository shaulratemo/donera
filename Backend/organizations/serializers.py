from rest_framework import serializers
from decimal import Decimal
from django.db.models import Sum
from django.db.models.functions import Coalesce

from donations.models import Donation
from .models import Organization
from users.serializers import UserSerializer

class OrganizationSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    causes_count = serializers.SerializerMethodField()
    active_causes_count = serializers.SerializerMethodField()
    total_amount_raised = serializers.SerializerMethodField()

    def get_causes_count(self, obj):
        annotated_value = getattr(obj, "causes_count", None)
        if annotated_value is not None:
            return annotated_value
        return obj.causes.count()

    def get_active_causes_count(self, obj):
        annotated_value = getattr(obj, "active_causes_count", None)
        if annotated_value is not None:
            return annotated_value
        return obj.causes.filter(status="ACTIVE").count()

    def get_total_amount_raised(self, obj):
        annotated_value = getattr(obj, "total_amount_raised", None)
        if annotated_value is not None:
            return annotated_value

        return Donation.objects.filter(
            cause__organization=obj,
            status="SUCCESS",
        ).aggregate(total=Coalesce(Sum("amount"), Decimal("0.00")))["total"]
    
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
            "causes_count",
            "active_causes_count",
            "total_amount_raised",
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