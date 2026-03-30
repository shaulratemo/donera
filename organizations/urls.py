from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import (
    OrganizationCreateView,
    MyOrganizationView,
    ApprovedOrganizationListView
)

urlpatterns = [
    path("register/", OrganizationCreateView.as_view(), name="org-register"),
    path("me/", MyOrganizationView.as_view(), name="org-me"),
    path("approved/", ApprovedOrganizationListView.as_view(), name="org-approved-list"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)