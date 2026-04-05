from django.db.models import Count, Sum
from causes.models import Cause
from donations.models import Donation
from rest_framework.response import Response
from rest_framework.views import APIView

from .permissions import IsOrganizationAdmin


class OrganizationDashboardView(APIView):
    permission_classes = [IsOrganizationAdmin]

    def get(self, request):
        organization = request.user.organization
        completed_donations = Donation.objects.filter(
            cause__organization=organization,
            status="SUCCESS",
        )

        donor_groups = completed_donations.values("user").annotate(
            donated_amount=Sum("amount")
        )

        data = {
            "overview": {
                "total_funds_raised": completed_donations.aggregate(total=Sum("amount"))["total"]
                or 0,
                "active_causes": Cause.objects.filter(
                    organization=organization,
                    status="ACTIVE",
                ).aggregate(total=Count("id"))["total"]
                or 0,
                "total_donors": donor_groups.aggregate(total=Count("user"))["total"]
                or 0,
                "pending_reports": 2,
            },
            "alerts": [],
        }

        return Response(data)