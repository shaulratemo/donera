from rest_framework import generics
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from .models import Report
from causes.models import Cause # We need to check the cause!
from .serializers import ReportSerializer
from users.permissions import IsOrganizationAdmin

# The Reports Feed (For Donors)
class PublishedReportListView(generics.ListAPIView):
    serializer_class = ReportSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        return Report.objects.filter(
            status="PUBLISHED",
            cause__organization__verification_status="APPROVED"
        ).order_by("-created_at")

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

# Managing a Report (For organizations editing Drafts or Publishing)
class OrganizationReportDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if hasattr(user, "orgnaization"):
            return Report.objects.filter(created_by=user)
        return Report.objects.none()