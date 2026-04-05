from django.urls import path
from .views import ActiveCauseListView, CauseCreateView, OrganizationCauseDetailView, PublicCauseDetailView
from reports.views import CauseReportListView

urlpatterns = [
    path("feed/", ActiveCauseListView.as_view(), name="cause-feed"),
    path("create/", CauseCreateView.as_view(), name="cause-create"),
    path("<int:id>/reports/", CauseReportListView.as_view(), name="cause-reports"),
    path("<int:pk>/", PublicCauseDetailView.as_view(), name="cause-detail"),
    path("<int:pk>/manage/", OrganizationCauseDetailView.as_view(), name="cause-manage"),
]
