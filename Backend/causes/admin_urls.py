from django.urls import path

from .views import AdminCauseListView

urlpatterns = [
    path("", AdminCauseListView.as_view(), name="admin-cause-list"),
]
