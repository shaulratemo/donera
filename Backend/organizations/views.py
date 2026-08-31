from django.utils import timezone
from decimal import Decimal
from django.db.models import Sum, Count, Q, DecimalField, Value
from django.db.models.functions import Coalesce
from rest_framework import generics, serializers, status
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.exceptions import ObjectDoesNotExist
from causes.models import Cause
from donations.models import Donation
from .models import Organization
from .serializers import OrganizationSerializer
from users.permissions import IsAdmin, IsOrganizationAdmin

# Registration View
class OrganizationCreateView(generics.CreateAPIView):
    serializer_class = OrganizationSerializer
    permission_classes = [IsOrganizationAdmin]
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

# Owner's Dashboard View
class MyOrganizationView(generics.RetrieveUpdateAPIView):
    serializer_class = OrganizationSerializer
    permission_classes = [IsOrganizationAdmin]
    
    def get_object(self):
        try:
            return self.request.user.organization
        except ObjectDoesNotExist:
            return None
        
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance:
            return Response(
                {"detail": "You do not have a registered organization."},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

# The Public List View
class ApprovedOrganizationListView(generics.ListAPIView):
    serializer_class = OrganizationSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        return Organization.objects.filter(verification_status='APPROVED')


class OrganizationVerificationSerializer(serializers.Serializer):
    verification_status = serializers.ChoiceField(choices=["APPROVED", "REJECTED"])


class PendingOrganizationListView(generics.ListAPIView):
    serializer_class = OrganizationSerializer
    permission_classes = [IsAdmin]

    def get_queryset(self):
        return Organization.objects.filter(verification_status="PENDING").order_by("-created_at")


class AdminOrganizationListView(generics.ListAPIView):
    serializer_class = OrganizationSerializer
    permission_classes = [IsAdmin]

    def get_queryset(self):
        return Organization.objects.annotate(
            causes_count=Count("causes", distinct=True),
            active_causes_count=Count("causes", filter=Q(causes__status="ACTIVE"), distinct=True),
            total_amount_raised=Coalesce(
                Sum(
                    "causes__donations__amount",
                    filter=Q(causes__donations__status="SUCCESS"),
                ),
                Value(Decimal("0.00")),
                output_field=DecimalField(max_digits=12, decimal_places=2),
            ),
        ).order_by("-created_at")


class OrganizationVerificationView(generics.UpdateAPIView):
    serializer_class = OrganizationSerializer
    permission_classes = [IsAdmin]
    queryset = Organization.objects.all()
    lookup_field = "id"
    http_method_names = ["patch"]

    def patch(self, request, *args, **kwargs):
        organization = self.get_object()
        payload = OrganizationVerificationSerializer(data=request.data)
        payload.is_valid(raise_exception=True)

        verification_status = payload.validated_data["verification_status"]
        organization.verification_status = verification_status
        organization.verified_at = timezone.now() if verification_status == "APPROVED" else None
        organization.save(update_fields=["verification_status", "verified_at", "updated_at"])

        return Response(self.get_serializer(organization).data, status=status.HTTP_200_OK)


class AdminDashboardStatsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        data = {
            "pending_verifications": Organization.objects.filter(verification_status="PENDING").count(),
            "total_verified_orgs": Organization.objects.filter(verification_status__in=["VERIFIED", "APPROVED"]).count(),
            "active_causes": Cause.objects.filter(status="ACTIVE").count(),
            "total_platform_volume": Donation.objects.aggregate(
                total=Coalesce(Sum("amount"), Decimal("0.00"))
            )["total"],
        }
        return Response(data)