from decimal import Decimal

from django.db.models import DecimalField, Q, Sum, Value
from django.db.models.functions import Coalesce
from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from .models import Cause
from .serializers import CauseSerializer
from users.permissions import IsOrganizationAdmin

# For the public List of causes
class ActiveCauseListView(generics.ListAPIView):
    serializer_class = CauseSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        return (
            Cause.objects.filter(
                status="ACTIVE",
                organization__verification_status="APPROVED",
            )
            .select_related("organization")
            .annotate(
                amount_raised_annotated=Coalesce(
                    Sum("donations__amount", filter=Q(donations__status="SUCCESS")),
                    Value(Decimal("0.00")),
                    output_field=DecimalField(max_digits=12, decimal_places=2),
                )
            )
        )


class PublicCauseDetailView(generics.RetrieveAPIView):
    serializer_class = CauseSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return (
            Cause.objects.filter(
                status="ACTIVE",
                organization__verification_status="APPROVED",
            )
            .select_related("organization")
            .annotate(
                amount_raised_annotated=Coalesce(
                    Sum("donations__amount", filter=Q(donations__status="SUCCESS")),
                    Value(Decimal("0.00")),
                    output_field=DecimalField(max_digits=12, decimal_places=2),
                )
            )
        )

    def retrieve(self, request, *args, **kwargs):
        cause = self.get_object()
        data = self.get_serializer(cause).data
        data["organization"] = {
            "id": cause.organization_id,
            "name": cause.organization.name,
            "verification_status": cause.organization.verification_status,
        }
        return Response(data)

# Cause Creation
class CauseCreateView(generics.CreateAPIView):
    serializer_class = CauseSerializer
    permission_classes = [IsOrganizationAdmin]
    
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
    permission_classes = [IsOrganizationAdmin]
    
    def get_queryset(self):
        user = self.request.user
        if hasattr(user, "organization"):
            return Cause.objects.filter(organization=user.organization)
        return Cause.objects.none() # Returns an empty list if they are not an organizations