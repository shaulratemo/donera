from django.urls import path
from .views import InitiateDonationView, MyDonationsListView, OrganizationDonationListView

urlpatterns = [
    # POST to trigger the STK push
    path('initiate/', InitiateDonationView.as_view(), name='donation-initiate'),
    path('history/', MyDonationsListView.as_view(), name='donation-history'),
    path('dashboard/', OrganizationDonationListView.as_view(), name='donation-dashboard'),
]