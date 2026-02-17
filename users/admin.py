from django.contrib import admin
from .models import User

# Register your models here.
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'full_name',
        'email',
        'role',
        'phone_number',
        'is_active',
        'is_staff',
    )
    
    list_filter = ('role', 'is_active', 'is_staff')
    search_fields = ('username', 'full_name', 'email', 'phone_number')