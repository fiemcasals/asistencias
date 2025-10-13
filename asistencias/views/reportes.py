import csv
from django.http import HttpResponse

from asistencias.models import Materia, InscripcionMateria
from asistencias.permissions import requiere_nivel


@requiere_nivel(3)
def exportar_reportes(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="reportes_asistencias.csv"'
    writer = csv.writer(response)
    writer.writerow(['Diplomatura', 'Materia', 'Clase(fecha-horario)', 'Alumno(dni)', 'Presente'])
    for mat in Materia.objects.select_related('diplomatura'):
        for c in mat.clases.all():
            presentes = set(c.asistencias.values_list('user__dni', flat=True))
            insc = InscripcionMateria.objects.filter(materia=mat).values_list('user__dni', flat=True)
            for dni in insc:
                writer.writerow([
                    mat.diplomatura.codigo, mat.nombre,
                    f"{c.fecha} {c.hora_inicio}-{c.hora_fin}",
                    dni, '1' if dni in presentes else '0'
                ])
    return response
