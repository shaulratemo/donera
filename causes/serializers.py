from rest_framework import serializers
from .models import Cause
from organizations.serializers import MiniOrganizationSerializer

class CauseSerializer(serializers.ModelSerializer):
    organization = MiniOrganizationSerializer(read_only=True)
    amount_raised = serializers.ReadOnlyField()
    
    class Meta:
        model = Cause
        fields = [
            "id",
            "organization",
            "title",
            "description",
            "category",
            "status",
            "target_amount",
            "amount_raised",
            "start_date",
            "end_date",
            "created_at",
            "updated_at"
        ]
        
        read_only_fields = ["id", "organization", "amount_raised", "created_at", "updated_at"]