from rest_framework import serializers
from decimal import Decimal

from causes.models import Cause

from .models import Donation
from users.serializers import MiniUserSerializer


class DonationSerializer(serializers.ModelSerializer):
    user = MiniUserSerializer(read_only=True)
    
    class Meta:
        model = Donation
        fields = [
            "id",
            "user",
            "cause",
            "amount",
            "phone_number",
            "currency",
            "status",
            "payment_method",
            "transaction_reference",
            "external_checkout_id",
            "failure_reason",
            "created_at",
            "updated_at",
            "completed_at"
        ]
        
        read_only_fields = [
            "id",
            "user",
            "status",
            "transaction_reference",
            "external_checkout_id",
            "failure_reason",
            "created_at",
            "updated_at",
            "completed_at"
        ]


class InitiateDonationSerializer(serializers.Serializer):
    cause_id = serializers.PrimaryKeyRelatedField(
        source="cause",
        queryset=Cause.objects.filter(status="ACTIVE"),
    )
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal("1.00"))
    phone_number = serializers.CharField(max_length=15)

    def validate_cause(self, cause):
        if cause.organization.verification_status != "APPROVED":
            raise serializers.ValidationError("Cause must belong to an approved organization.")
        return cause