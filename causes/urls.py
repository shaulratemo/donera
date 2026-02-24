from django.urls import path
from .views import ActiveCauseListView, CauseCreateView, OrganizationCauseDetailView

urlpatterns = [
    path("feed/", ActiveCauseListView.as_view(), name="cause-feed"),
    path("create/", CauseCreateView.as_view(), name="cause-create"),
    path("<int:pk>/manage/", OrganizationCauseDetailView.as_view(), name="cause-manage"),
]
