from rest_framework import serializers
from .models import Report

class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = [
            "id",
            "cause",
            "created_by",
            "content",
            "summary",
            "evidence",
            "status",
            "created_at",
            "updated_at"
        ]
        
        read_only_fields = [
            "id",
            "created_by",
            "summary",
            "created_at",
            "updated_at"
        ]