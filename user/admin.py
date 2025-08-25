from django.contrib import admin
from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('nickname', 'name', 'phone', 'openid', 'created_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('nickname', 'name', 'phone', 'openid')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('基本信息', {
            'fields': ('nickname', 'name', 'phone', 'address')
        }),
        ('微信信息', {
            'fields': ('openid',)
        }),
        ('头像', {
            'fields': ('avatar',)
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
