from uuid import uuid4

from django.utils import timezone
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Donation
from .serializers import DonationSerializer, InitiateDonationSerializer
from users.permissions import IsSystemAdmin


class InitiateDonationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = InitiateDonationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        donation = Donation.objects.create(
            user=self.request.user,
            cause=serializer.validated_data["cause"],
            amount=serializer.validated_data["amount"],
            phone_number=serializer.validated_data["phone_number"],
            status="PENDING",
        )
        checkout_request_id = f"ws_CO_{uuid4().hex}"
        donation.external_checkout_id = checkout_request_id
        donation.save(update_fields=["external_checkout_id", "updated_at"])

        return Response(
            {
                "message": "STK push initiated (simulated).",
                "CheckoutRequestID": checkout_request_id,
                "status": donation.status,
                "donation": DonationSerializer(donation).data,
            },
            status=status.HTTP_201_CREATED,
        )


class DonationWebhookView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        checkout_request_id = self._extract_checkout_request_id(request.data)
        if not checkout_request_id:
            return Response(
                {"detail": "CheckoutRequestID is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        donation = Donation.objects.filter(external_checkout_id=checkout_request_id).first()
        if not donation:
            return Response(
                {"detail": "Donation not found for provided CheckoutRequestID."},
                status=status.HTTP_404_NOT_FOUND,
            )

        donation.status = "SUCCESS"
        if donation.completed_at is None:
            donation.completed_at = timezone.now()
        donation.save(update_fields=["status", "completed_at", "updated_at"])

        return Response(
            {
                "message": "Webhook processed (simulated).",
                "CheckoutRequestID": checkout_request_id,
                "status": donation.status,
            },
            status=status.HTTP_200_OK,
        )

    @staticmethod
    def _extract_checkout_request_id(payload):
        if not isinstance(payload, dict):
            return None
        if payload.get("CheckoutRequestID"):
            return payload.get("CheckoutRequestID")

        body = payload.get("Body") or {}
        stk_callback = body.get("stkCallback") or {}
        return stk_callback.get("CheckoutRequestID")


class DonationStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, checkout_request_id=None):
        checkout_request_id = checkout_request_id or request.query_params.get("checkout_id")
        if not checkout_request_id:
            return Response(
                {"detail": "checkout_id is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        donation = Donation.objects.filter(
            user=request.user,
            external_checkout_id=checkout_request_id,
        ).first()

        if not donation:
            return Response(
                {"detail": "Donation not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            {
                "CheckoutRequestID": checkout_request_id,
                "status": donation.status,
                "donation_id": donation.id,
                "amount": donation.amount,
                "cause_id": donation.cause_id,
            },
            status=status.HTTP_200_OK,
        )


# Donor donations history
class MyDonationsListView(generics.ListAPIView):
    serializer_class = DonationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Donation.objects.filter(user=self.request.user).order_by("-created_at")

# Organization Dashboard
class OrganizationDonationListView(generics.ListAPIView):
    serializer_class = DonationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        # Check whether they are an organization owner
        if hasattr(user, "organization"):
            return Donation.objects.filter(
                cause__organization=user.organization,
                status="SUCCESS"
            ).order_by("-created_at")
        
        return Donation.objects.none()


class AdminDonationLedgerListView(generics.ListAPIView):
    serializer_class = DonationSerializer
    permission_classes = [IsSystemAdmin]

    def get_queryset(self):
        return Donation.objects.all().order_by("-created_at")