from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import PermissionDenied
from .models import Report
from causes.models import Cause # We need to check the cause!
from .serializers import ReportSerializer

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
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        user = self.request.user
        
        # Check if they are an approved organization
        if not hasattr(user, "organization") or user.organization.verification_status != "APPROVED":
            raise PermissionDenied("Only approved organizations can submit reports.")
        
        cause_id = self.request.data.get('cause')
        try:
            cause = Cause.objects.get(id=cause_id, organization=user.organization)
        except Cause.DoesNotExist:
            raise PermissionDenied("You can only create reports for causes owned by our organization.")
        
        # --- AI INTEGRATION POINT ---
        # We extract the long content the organization typed
        content = serializer.validated_data.get("content", "")
        
        # Later, you will pass this content to your Python AI function (e.g., using spaCy/NLTK or an API)
        # generated_summary = generate_ai_summary(content) 
        generated_summary = "AI generated summary placeholder." 

        # The Injection: Save the report with the safe user and the AI summary
        serializer.save(
            created_by=user,
            summary=generated_summary
        )

# Managing a Report (For organizations editing Drafts or Publishing)
class OrganizationReportDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if hasattr(user, "orgnaization"):
            return Report.objects.filter(created_by=user)
        return Report.objects.none()