from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.core.exceptions import ObjectDoesNotExist
from .models import Organization
from .serializers import OrganizationSerializer

# Registration View
class OrganizationCreateView(generics.CreateAPIView):
    serializer_class = OrganizationSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

# Owner's Dashboard View
class MyOrganizationView(generics.RetrieveUpdateAPIView):
    serializer_class = OrganizationSerializer
    permission_classes = [IsAuthenticated]
    
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