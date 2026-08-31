from django.urls import path
from .views import (
    ActiveCauseListView,
    CauseCreateView,
    OrganizationCauseListView,
    OrganizationCauseDetailView,
    PublicCauseDetailView,
    RecommendedCauseListView,
)
from reports.views import CauseReportListView

urlpatterns = [
    path("", ActiveCauseListView.as_view(), name="cause-list"),
    path("feed/", ActiveCauseListView.as_view(), name="cause-feed"),
    path("organization/", OrganizationCauseListView.as_view(), name="organization-cause-list"),
    path("recommended/", RecommendedCauseListView.as_view(), name="cause-recommended"),
    path("create/", CauseCreateView.as_view(), name="cause-create"),
    path("<int:id>/reports/", CauseReportListView.as_view(), name="cause-reports"),
    path("<int:pk>/", PublicCauseDetailView.as_view(), name="cause-detail"),
    path("<int:pk>/manage/", OrganizationCauseDetailView.as_view(), name="cause-manage"),
]
