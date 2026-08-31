from django.contrib import admin
from .models import Donation

# Register your models here.
@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "cause", "amount", "currency", "status", "payment_method", "created_at")
    list_filter = ("status", "payment_method", "currency")
    search_fields = ("user__username", "user__full_name", "phone_number", "transaction_reference", "external_checkout_id")