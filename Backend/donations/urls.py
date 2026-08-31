from django.urls import path

from .views import (
    DonationStatusView,
    DonationWebhookView,
    InitiateDonationView,
    MyDonationsListView,
    OrganizationDonationListView,
)

urlpatterns = [
    # POST to trigger the STK push
    path('initiate/', InitiateDonationView.as_view(), name='donation-initiate'),
    path('webhook/', DonationWebhookView.as_view(), name='donation-webhook'),
    path('status/', DonationStatusView.as_view(), name='donation-status-query'),
    path('status/<str:checkout_request_id>/', DonationStatusView.as_view(), name='donation-status'),
    path('history/', MyDonationsListView.as_view(), name='donation-history'),
    path('dashboard/', OrganizationDonationListView.as_view(), name='donation-dashboard'),
]