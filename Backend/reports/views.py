from rest_framework import generics
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from .models import Report
from causes.models import Cause # We need to check the cause!
from .serializers import (
    ReportSerializer,
    PublicReportSerializer,
    RecentReportSerializer,
    CauseWithReportsSerializer,
    AdminPendingReportSerializer,
    AdminReportDetailSerializer,
)
from users.permissions import IsOrganizationAdmin, IsSystemAdmin

# The Reports Feed (For Donors)
class PublishedReportListView(generics.ListAPIView):
    serializer_class = PublicReportSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        return (
            Report.objects.filter(
                status="PUBLISHED",
                cause__organization__verification_status="APPROVED",
            )
            .select_related("cause", "cause__organization")
            .order_by("-created_at")
        )

# Create a Report (For Organizations)
class ReportCreateView(generics.CreateAPIView):
    serializer_class = ReportSerializer
    permission_classes = [IsOrganizationAdmin]
    parser_classes = [MultiPartParser, FormParser]
    
    def perform_create(self, serializer):
        user = self.request.user
        
        # Check if they are an approved organization
        if not hasattr(user, "organization") or user.organization.verification_status != "APPROVED":
            raise PermissionDenied("Only approved organizations can submit reports.")
        
        cause = serializer.validated_data.get("cause")
        try:
            Cause.objects.get(id=cause.id, organization=user.organization)
        except Cause.DoesNotExist:
            raise PermissionDenied("You can only create reports for causes owned by your organization.")

        serializer.save(created_by=user)


class CauseReportListView(generics.ListAPIView):
    serializer_class = ReportSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Report.objects.filter(
            cause_id=self.kwargs["id"],
            status="PUBLISHED",
        ).order_by("-created_at")


class RecentReportListView(generics.ListAPIView):
    serializer_class = RecentReportSerializer
    permission_classes = [IsOrganizationAdmin]

    def get_queryset(self):
        return (
            Report.objects.filter(created_by=self.request.user)
            .select_related("cause")
            .order_by("-created_at")[:5]
        )


class GroupedReportsByCauseView(generics.ListAPIView):
    serializer_class = CauseWithReportsSerializer
    permission_classes = [IsOrganizationAdmin]

    def get_queryset(self):
        return (
            Cause.objects.filter(organization__owner=self.request.user)
            .prefetch_related("reports")
            .order_by("-created_at")
        )

# Managing a Report (For organizations editing Drafts or Publishing)
class OrganizationReportDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = ReportSerializer
    permission_classes = [IsOrganizationAdmin]
    
    def get_queryset(self):
        user = self.request.user
        if hasattr(user, "organization"):
            return Report.objects.filter(created_by=user)
        return Report.objects.none()


# Admin endpoints for system admin to review and approve/decline reports
class AdminPendingReportListView(generics.ListAPIView):
    serializer_class = AdminPendingReportSerializer
    permission_classes = [IsSystemAdmin]

    def get_queryset(self):
        return (
            Report.objects.filter(status="DRAFT")
            .select_related("cause", "cause__organization")
            .order_by("created_at")
        )


class AdminReportDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = AdminReportDetailSerializer
    permission_classes = [IsSystemAdmin]
    http_method_names = ["get", "patch", "head", "options"]

    def get_queryset(self):
        return Report.objects.all()

    def perform_update(self, serializer):
        # Only allow status updates during PATCH/PUT
        if "status" in serializer.validated_data:
            serializer.save()
        else:
            raise PermissionDenied("Only status field can be updated by admin.")