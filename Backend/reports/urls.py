from django.urls import path
from .views import (
    PublishedReportListView,
    ReportCreateView,
    OrganizationReportDetailView,
    RecentReportListView,
    GroupedReportsByCauseView,
)

urlpatterns = [
    path("", ReportCreateView.as_view(), name="report-submit"),
    path("feed/", PublishedReportListView.as_view(), name="report-feed"),
    path("public/", PublishedReportListView.as_view(), name="report-public"),
    path("recent/", RecentReportListView.as_view(), name="report-recent"),
    path("grouped-by-cause/", GroupedReportsByCauseView.as_view(), name="reports-grouped-by-cause"),
    path("create/", ReportCreateView.as_view(), name="report-create"),
    path("<int:pk>/", OrganizationReportDetailView.as_view(), name="report-manage"),
]