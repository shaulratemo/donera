from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Donation
from .serializers import DonationSerializer

# For initiationg Donation (For Donors)
class InitiateDonationView(generics.CreateAPIView):
    serializer_class = DonationSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        # Firstly save the donation record to the database safely
        # Explicitly declare the status of the donation to 'PENDING' to prevent frontend manipulation of the donation status
        donation = serializer.save(
            user=self.request.user,
            status="PENDING"
        )
        
        # Add the Daraja API STK Push logic
        # 2. At this exact spot, you will write a Python function that takes:
        #    - donation.phone_number
        #    - donation.amount
        #    And sends an HTTP request to Safaricom's Daraja API.
        
        # 3. Safaricom will respond instantly with a CheckoutRequestID.
        # You will save that ID to the database so you can track it later:
        # donation.external_checkout_id = mpesa_response['CheckoutRequestID']
        # donation.save()
    
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