from rest_framework import serializers
from .models import Report
from .nlp import generate_report_summary
from causes.models import Cause

class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = [
            "id",
            "cause",
            "created_by",
            "funds_utilized",
            "expense_category",
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

    def create(self, validated_data):
        content = validated_data.get("content", "")
        validated_data["summary"] = generate_report_summary(content)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if instance.status == "PUBLISHED":
            raise serializers.ValidationError("Approved reports cannot be edited.")

        content = validated_data.get("content", instance.content)
        if "content" in validated_data and content != instance.content:
            validated_data["summary"] = generate_report_summary(content)

        return super().update(instance, validated_data)


class PublicReportSerializer(serializers.ModelSerializer):
    cause_name = serializers.CharField(source="cause.title", read_only=True)
    organization_name = serializers.CharField(source="cause.organization.name", read_only=True)
    evidence = serializers.SerializerMethodField()

    class Meta:
        model = Report
        fields = [
            "id",
            "created_at",
            "funds_utilized",
            "summary",
            "cause_name",
            "organization_name",
            "evidence",
        ]

    def get_evidence(self, obj):
        if not obj.evidence:
            return None

        request = self.context.get("request")
        url = obj.evidence.url
        if request is not None:
            return request.build_absolute_uri(url)
        return url


class RecentReportSerializer(serializers.ModelSerializer):
    cause_name = serializers.CharField(source="cause.title", read_only=True)
    created_at = serializers.DateTimeField(format="%b %d, %Y", read_only=True)

    class Meta:
        model = Report
        fields = [
            "id",
            "cause_name",
            "created_at",
            "status",
        ]


class GroupedCauseReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = [
            "id",
            "created_at",
            "status",
            "funds_utilized",
            "summary",
            "content",
            "expense_category",
        ]


class CauseWithReportsSerializer(serializers.ModelSerializer):
    reports = GroupedCauseReportSerializer(many=True, read_only=True)

    class Meta:
        model = Cause
        fields = [
            "id",
            "title",
            "status",
            "reports",
        ]


class AdminPendingReportSerializer(serializers.ModelSerializer):
    cause_name = serializers.CharField(source="cause.title", read_only=True)
    organization_name = serializers.CharField(source="cause.organization.name", read_only=True)

    class Meta:
        model = Report
        fields = [
            "id",
            "cause_name",
            "organization_name",
            "created_at",
            "status",
        ]
        read_only_fields = ["id", "cause_name", "organization_name", "created_at", "status"]


class AdminReportDetailSerializer(serializers.ModelSerializer):
    cause_name = serializers.CharField(source="cause.title", read_only=True)
    organization_name = serializers.CharField(source="cause.organization.name", read_only=True)
    evidence = serializers.SerializerMethodField()

    class Meta:
        model = Report
        fields = [
            "id",
            "cause_name",
            "organization_name",
            "content",
            "summary",
            "funds_utilized",
            "expense_category",
            "evidence",
            "status",
        ]
        read_only_fields = ["id", "cause_name", "organization_name", "content", "summary", "funds_utilized", "expense_category", "evidence"]

    def get_evidence(self, obj):
        if not obj.evidence:
            return None

        request = self.context.get("request")
        url = obj.evidence.url
        if request is not None:
            return request.build_absolute_uri(url)
        return url

    def validate_status(self, value):
        if value not in ["PUBLISHED", "DECLINED"]:
            raise serializers.ValidationError("Status can only be set to PUBLISHED or DECLINED.")
        return value