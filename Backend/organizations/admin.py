from django.contrib import admin
from .models import Organization

# Register your models here.
@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("name", "registration_number", "verification_status", "verified_at", "contact_email")
    list_filter = ("verification_status",)
    search_fields = ("name", "registration_number", "contact_email")