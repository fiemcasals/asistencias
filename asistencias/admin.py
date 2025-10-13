# asistencias/admin.py
from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import (
    AccesoToken, Diplomatura, Materia, Clase, Asistencia,
    InscripcionDiplomatura, InscripcionMateria, ProfesorMateria
)

UserModel = get_user_model()

@admin.register(UserModel)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "dni", "nivel", "first_name", "last_name", "is_active", "is_staff")
    list_filter  = ("nivel", "is_active", "is_staff")
    search_fields = ("email", "dni", "first_name", "last_name")

@admin.register(Diplomatura)
class DiplomaturaAdmin(admin.ModelAdmin):
    list_display = ("id", "codigo", "nombre")
    search_fields = ("codigo", "nombre")

@admin.register(Materia)
class MateriaAdmin(admin.ModelAdmin):
    list_display = ("id", "codigo", "nombre", "diplomatura", "profesor_titular")
    search_fields = ("codigo", "nombre", "diplomatura__nombre")
    autocomplete_fields = ("diplomatura", "profesor_titular")

@admin.register(Clase)
class ClaseAdmin(admin.ModelAdmin):
    list_display = ("id", "materia", "fecha", "hora_inicio", "hora_fin", "tema")
    list_filter  = ("fecha", "materia")
    autocomplete_fields = ("materia",)
    # NECESARIO por el autocomplete que te pide Django
    search_fields = ("materia__nombre", "materia__diplomatura__nombre", "tema")

@admin.register(Asistencia)
class AsistenciaAdmin(admin.ModelAdmin):
    list_display = ("id", "clase", "user", "presente", "timestamp")
    list_filter  = ("presente", "clase__materia")
    autocomplete_fields = ("clase", "user")  # ← exige search_fields en ClaseAdmin y UserAdmin

@admin.register(InscripcionDiplomatura)
class InscripcionDiplomaturaAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "diplomatura", "fecha")  # ← era created_at; en tu modelo es 'fecha'
    search_fields = ("user__email", "diplomatura__nombre")
    autocomplete_fields = ("user", "diplomatura")

@admin.register(InscripcionMateria)
class InscripcionMateriaAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "materia", "fecha")  # ← era created_at; en tu modelo es 'fecha'
    search_fields = ("user__email", "materia__nombre")
    autocomplete_fields = ("user", "materia")

@admin.register(ProfesorMateria)
class ProfesorMateriaAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "materia", "rol")
    list_filter  = ("rol",)
    autocomplete_fields = ("user", "materia")

@admin.register(AccesoToken)
class AccesoTokenAdmin(admin.ModelAdmin):
    list_display = ("code", "nivel_destino", "activo", "expires_at", "usado_por", "usado_en", "creado_por")
    list_filter  = ("nivel_destino", "activo")
    search_fields = ("code", "usado_por__email", "creado_por__email")
    readonly_fields = ("usado_en",)
    autocomplete_fields = ("creado_por", "usado_por")

    actions = ["regenerar_codigo", "activar_tokens", "desactivar_tokens"]

    def regenerar_codigo(self, request, queryset):
        n = 0
        for tok in queryset:
            tok.regenerar()
            n += 1
        self.message_user(request, f"Se regeneraron {n} código(s).")
    regenerar_codigo.short_description = "Regenerar código"

    def activar_tokens(self, request, queryset):
        updated = queryset.update(activo=True)
        self.message_user(request, f"Se activaron {updated} token(s).")
    activar_tokens.short_description = "Activar"

    def desactivar_tokens(self, request, queryset):
        updated = queryset.update(activo=False)
        self.message_user(request, f"Se desactivaron {updated} token(s).")
    desactivar_tokens.short_description = "Desactivar"
