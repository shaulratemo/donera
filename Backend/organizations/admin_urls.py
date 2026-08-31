from django.urls import path

from .views import (
    AdminDashboardStatsView,
    PendingOrganizationListView,
    OrganizationVerificationView,
    AdminOrganizationListView,
)

urlpatterns = [
    path("stats/", AdminDashboardStatsView.as_view(), name="admin-dashboard-stats"),
    path("all/", AdminOrganizationListView.as_view(), name="admin-org-all"),
    path("pending/", PendingOrganizationListView.as_view(), name="admin-org-pending"),
    path("<int:id>/verify/", OrganizationVerificationView.as_view(), name="admin-org-verify"),
]
