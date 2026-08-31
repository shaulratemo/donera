from decimal import Decimal

from django.db.models import Case, DecimalField, IntegerField, Q, Sum, Value, When
from django.db.models.functions import Coalesce
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from .models import Cause
from .recommender import get_cause_recommendations
from .serializers import CauseSerializer
from users.permissions import IsAdmin, IsOrganizationAdmin

# For the public List of causes
class ActiveCauseListView(generics.ListAPIView):
    serializer_class = CauseSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        return (
            Cause.objects
            .select_related("organization")
            .filter(
                status="ACTIVE",
                organization__verification_status="APPROVED",
            )
            .annotate(
                amount_raised_annotated=Coalesce(
                    Sum("donations__amount", filter=Q(donations__status="SUCCESS")),
                    Value(Decimal("0.00")),
                    output_field=DecimalField(max_digits=12, decimal_places=2),
                )
            )
            .order_by("-created_at")
        )


class OrganizationCauseListView(generics.ListAPIView):
    serializer_class = CauseSerializer
    permission_classes = [IsOrganizationAdmin]

    def get_queryset(self):
        queryset = (
            Cause.objects
            .select_related("organization")
            .filter(organization__owner=self.request.user)
            .annotate(
                amount_raised_annotated=Coalesce(
                    Sum("donations__amount", filter=Q(donations__status="SUCCESS")),
                    Value(Decimal("0.00")),
                    output_field=DecimalField(max_digits=12, decimal_places=2),
                )
            )
        )

        status_filter = (self.request.query_params.get("status") or "").upper()
        if status_filter in {"ACTIVE", "PAUSED", "COMPLETED"}:
            queryset = queryset.filter(status=status_filter)

        return queryset.order_by("-created_at")


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


class AdminCauseListView(generics.ListAPIView):
    serializer_class = CauseSerializer
    permission_classes = [IsAdmin]

    def get_queryset(self):
        queryset = (
            Cause.objects
            .select_related("organization")
            .annotate(
                amount_raised_annotated=Coalesce(
                    Sum("donations__amount", filter=Q(donations__status="SUCCESS")),
                    Value(Decimal("0.00")),
                    output_field=DecimalField(max_digits=12, decimal_places=2),
                )
            )
            .order_by("-created_at")
        )

        status_filter = (self.request.query_params.get("status") or "").upper()
        if status_filter in {"ACTIVE", "PAUSED", "COMPLETED"}:
            queryset = queryset.filter(status=status_filter)

        return queryset


class RecommendedCauseListView(generics.ListAPIView):
    serializer_class = CauseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        recommended_ids = get_cause_recommendations(self.request.user)
        if not recommended_ids:
            return Cause.objects.none()

        ordering = Case(
            *[When(id=cause_id, then=position) for position, cause_id in enumerate(recommended_ids)],
            output_field=IntegerField(),
        )

        return (
            Cause.objects.filter(
                id__in=recommended_ids,
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
            .order_by(ordering)
        )

