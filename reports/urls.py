from django.urls import path
from .views import PublishedReportListView, ReportCreateView, OrganizationReportDetailView

urlpatterns = [
    path("feed/", PublishedReportListView.as_view(), name="report-feed"),
    path("create/", ReportCreateView.as_view(), name="report-create"),
    path("<int:pk", OrganizationReportDetailView.as_view(), name="report-manage"),
]