from django.urls import path
from views import (
    OrganizationCreateView,
    MyOrganizationView,
    ApprovedOrganizationListView
)

urlpatterns = [
    path("register/", OrganizationCreateView.as_view(), name="org-register"),
    path("me/", MyOrganizationView.as_view(), name="org-me"),
    path("approved/", ApprovedOrganizationListView.as_view(), name="org-approved-list"),
]
