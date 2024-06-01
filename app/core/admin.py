from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from core import models
from django.utils.translation import gettext_lazy as _  # best Practice

# Register your models here.


class UserAdmin(BaseUserAdmin):
    ordering = ['id']
    list_display = ['email', 'name']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (
            _('Permissions'),
            {
                'fields': (
                    'is_staff',
                    'is_active',
                    'is_superuser',
                )
            }
        ),
        (_('Imporatant dates'), {'fields': ('last_login',)})
    )
    readonly_fields = ['last_login',]
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email',
                'password1',
                'password2',
                'name',
                'is_staff',
                'is_active',
                'is_superuser',
            ),
        }),
    )


admin.site.register(models.User, UserAdmin)
