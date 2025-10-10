from django.urls import path
from . import views

app_name = 'asistencias'

urlpatterns = [
    path('', views.home, name='home'),
    path('publico/', views.publico, name='publico'),
    path('publico/marcar/<int:clase_id>/', views.marcar_presente, name='marcar_presente'),
    path('publico/consulta/', views.consulta_asistencias, name='consulta_asistencias'),
    path('gestion/', views.gestion, name='gestion'),
    path('gestion/diplomatura/nueva/', views.diplomatura_nueva, name='diplomatura_nueva'),
    path('gestion/materia/nueva/', views.materia_nueva, name='materia_nueva'),
    path('gestion/clase/nueva/', views.clase_nueva, name='clase_nueva'),
    path('gestion/materia/<int:materia_id>/clases/', views.listado_clases, name='listado_clases'),
    path('gestion/materia/<int:materia_id>/asistencias/pdf/', views.exportar_asistencias_pdf, name='exportar_asistencias_pdf'),
]
