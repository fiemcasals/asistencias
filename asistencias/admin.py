from django.contrib import admin
from .models import Diplomatura, Materia, Alumno, Clase, Asistencia

@admin.register(Diplomatura)
class DiplomaturaAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)

@admin.register(Materia)
class MateriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'diplomatura')
    list_filter = ('diplomatura',)
    search_fields = ('nombre',)

@admin.register(Alumno)
class AlumnoAdmin(admin.ModelAdmin):
    list_display = ('dni', 'apellido1', 'nombre1', 'correo')
    search_fields = ('dni', 'apellido1', 'nombre1')

@admin.register(Clase)
class ClaseAdmin(admin.ModelAdmin):
    list_display = ('materia', 'fecha', 'inicio_habilitacion', 'fin_habilitacion', 'tema')
    list_filter = ('materia__diplomatura', 'materia', 'fecha')
    search_fields = ('materia__nombre', 'tema')

@admin.register(Asistencia)
class AsistenciaAdmin(admin.ModelAdmin):
    list_display = ('clase', 'alumno', 'presente', 'timestamp')
    list_filter = ('clase__materia__diplomatura', 'clase__materia', 'clase__fecha')
    search_fields = ('alumno__dni', 'alumno__apellido1', 'alumno__nombre1')
