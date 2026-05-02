from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Administrateur, AgentAdministratif, Demandeur, ProfilDemandeur


class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Informations spécifiques', {
            'fields': ('role', 'statut', 'date_creation')
        }),
    )

    readonly_fields = ('date_creation',)

    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'role',
        'statut',
        'is_staff'
    )

    list_filter = (
        'role',
        'statut',
        'is_staff',
        'is_superuser',
        'is_active'
    )


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Administrateur)
admin.site.register(AgentAdministratif)
admin.site.register(Demandeur)
admin.site.register(ProfilDemandeur)
