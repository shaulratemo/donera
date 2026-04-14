from django.urls import path

from .views import DonationStatusView, InitiateDonationView

urlpatterns = [
    path("initiate/", InitiateDonationView.as_view(), name="payment-initiate"),
    path("status/", DonationStatusView.as_view(), name="payment-status"),
]
