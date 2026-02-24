from rest_framework import serializers
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