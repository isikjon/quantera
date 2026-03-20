from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, PasswordResetToken, AuditLog


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'full_name', 'role', 'is_active', 'date_joined')
    list_filter = ('role', 'is_active', 'is_staff', 'is_2fa_enabled')
    search_fields = ('email', 'full_name', 'phone')
    ordering = ('-date_joined',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Личные данные', {'fields': ('full_name', 'phone', 'date_of_birth', 'telegram_id')}),
        ('Партнёрка', {'fields': ('referral_code', 'referred_by')}),
        ('Права', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'is_2fa_enabled')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'full_name', 'role'),
        }),
    )


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'code', 'created_at', 'is_used')
    list_filter = ('is_used',)


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'ip_address', 'created_at')
    list_filter = ('action',)
    search_fields = ('user__email', 'details')
    readonly_fields = ('user', 'action', 'details', 'ip_address', 'created_at')
