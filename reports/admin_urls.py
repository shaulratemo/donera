from django.urls import path

from .views import AdminPendingReportListView, AdminReportDetailView

urlpatterns = [
    path("pending/", AdminPendingReportListView.as_view(), name="admin-reports-pending"),
    path("<int:pk>/", AdminReportDetailView.as_view(), name="admin-report-detail"),
]
