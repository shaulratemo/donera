from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import PermissionDenied
from .models import Cause
from .serializers import CauseSerializer

# For the public List of causes
class ActiveCauseListView(generics.ListAPIView):
    serializer_class = CauseSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        return Cause.objects.filter(
            status="ACTIVE",
            organization__verification_status="APPROVED"
        )

# Cause Creation
class CauseCreateView(generics.CreateAPIView):
    serializer_class = CauseSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        user = self.request.user
        
        # Check if the user has an organization
        if not hasattr(user, 'organization'):
            raise PermissionDenied("You must register an organization before creating a cause.")
        
        # Check if the organization has been officially verified
        if user.organization.verification_status != "APPROVED":
            raise PermissionDenied("Your organization must be approved by an admin to create causes.")
        
        serializer.save(organization=user.organization)

# Cause management
class OrganizationCauseDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = CauseSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if hasattr(user, "organization"):
            return Cause.objects.filter(organization=user.organization)
        return Cause.objects.none() # Returns an empty list if they are not an organizations