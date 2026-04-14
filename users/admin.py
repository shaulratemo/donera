from django.contrib import admin
from .models import User, UserProfile

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


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'interests_display', 'is_onboarded', 'created_at')
    list_filter = ('is_onboarded', 'created_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')
    filter_horizontal = ('interests',)
    readonly_fields = ('created_at', 'updated_at')

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('user').prefetch_related('interests')

    def interests_display(self, obj):
        interests = [interest.name for interest in obj.interests.all()]
        return ', '.join(interests) if interests else '-'

    interests_display.short_description = 'Selected Interests'
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Interests', {
            'fields': ('interests',)
        }),
        ('Onboarding', {
            'fields': ('is_onboarded',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )