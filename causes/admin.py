from django.contrib import admin
from .models import Cause

# Register your models here.
@admin.register(Cause)
class CauseAdmin(admin.ModelAdmin):
    list_display = ("title", "organization", "category", "status", "target_amount", "created_at")
    list_filter = ("status", "category")
    search_fields = ("title", "organization__name", "category")