from django.contrib import admin
from .models import Registration, Invitation

@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ('user', 'event', 'status', 'is_verified', 'created_at')
    list_filter = ('status', 'is_verified', 'created_at')
    search_fields = ('user__username', 'user__email', 'phone_number')
    raw_id_fields = ('user', 'invited_by')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'phone_number', 'birth_date')
        }),
        ('Registration Details', {
            'fields': ('event', 'status', 'is_verified')
        }),
        ('Invitation Information', {
            'fields': ('invited_by', 'verification_token'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )
    
    readonly_fields = ('created_at',)

@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    list_display = ('email', 'registration', 'invitation_type', 'status', 'created_at', 'expires_at')
    list_filter = ('invitation_type', 'status', 'created_at')
    search_fields = ('email', 'registration__user__username')
    raw_id_fields = ('registration',)
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Invitation Details', {
            'fields': ('registration', 'email', 'invitation_type')
        }),
        ('Status Information', {
            'fields': ('status', 'token')
        }),
        ('Timing', {
            'fields': ('created_at', 'expires_at'),
            'classes': ('collapse',)
        })
    )
    
    readonly_fields = ('token', 'created_at')
