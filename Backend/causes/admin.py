from django.contrib import admin
from .models import Cause

# Register your models here.
@admin.register(Cause)
class CauseAdmin(admin.ModelAdmin):
    list_display = ("title", "organization", "category", "status", "target_amount", "created_at")
    list_filter = ("status", "category")
    search_fields = ("title", "organization__name", "category")
    fieldsets = (
        ("Basic Information", {
            "fields": ("organization", "title", "description", "cover_image", "category")
        }),
        ("Campaign Details", {
            "fields": ("status", "target_amount", "start_date", "end_date")
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )
    readonly_fields = ("created_at", "updated_at")