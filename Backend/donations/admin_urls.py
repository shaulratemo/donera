from django.urls import path

from .views import AdminDonationLedgerListView

urlpatterns = [
    path("", AdminDonationLedgerListView.as_view(), name="admin-donations-ledger"),
]
