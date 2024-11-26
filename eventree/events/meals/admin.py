from django.contrib import admin
from .models import Meal, MealSelection

@admin.register(Meal)
class MealAdmin(admin.ModelAdmin):
    list_display = ('name', 'event', 'meal_type', 'dietary_restriction', 'available_quantity', 'is_active')
    list_filter = ('event', 'meal_type', 'dietary_restriction', 'is_active')
    search_fields = ('name', 'description', 'event__title')
    ordering = ('event', 'meal_type', 'name')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('event', 'name', 'description')
        }),
        ('Meal Details', {
            'fields': ('meal_type', 'dietary_restriction', 'available_quantity', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(MealSelection)
class MealSelectionAdmin(admin.ModelAdmin):
    list_display = ('registration', 'meal', 'quantity', 'created_at')
    list_filter = ('meal__event', 'meal__meal_type', 'meal__dietary_restriction')
    search_fields = ('registration__user__username', 'meal__name', 'special_requests')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('registration', 'meal')
    fieldsets = (
        ('Selection Details', {
            'fields': ('registration', 'meal', 'quantity')
        }),
        ('Additional Information', {
            'fields': ('special_requests',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
