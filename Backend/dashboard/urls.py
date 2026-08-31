from django.urls import path

from .views import OrganizationDashboardView

urlpatterns = [
    path("organization/me/", OrganizationDashboardView.as_view(), name="organization-dashboard"),
]