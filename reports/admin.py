from django.contrib import admin
from .models import Report

# Register your models here.
@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ("id", "cause", "status", "created_by", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("cause__title", "content", "summary", "created_by__username", "created_by__full_name")