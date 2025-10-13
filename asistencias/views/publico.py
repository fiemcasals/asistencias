from django.shortcuts import render
from django.utils import timezone
from django.contrib import messages
from asistencias.models import Clase, Asistencia, User
from django.db.models import Q
from asistencias.models import Clase

def publico(request):
    now = timezone.localtime()

    # Clases activas ahora (ventana abierta)
    clases = (Clase.objects
              .select_related('materia', 'materia__diplomatura')
              .filter(hora_inicio__lte=now, hora_fin__gte=now))

    # Si está logueado: mostrar SOLO donde está inscripto o es profesor
    if request.user.is_authenticated:
        clases = (clases.filter(
                    Q(materia__inscripciones__user=request.user) |   # alumno inscripto
                    Q(materia__profesores__user=request.user)        # o profesor
                 ).distinct())
    else:
        # Si no está logueado, no mostramos nada (o podrías redirigir a login)
        clases = clases.none()

    clases = clases.order_by('materia__diplomatura__nombre',
                             'materia__nombre', 'hora_inicio')

    return render(request, 'asistencias/publico.html', {'clases': clases})
def consulta_publica(request):
    """
    - Alumno logueado (nivel 1): ignora DNI y muestra SUS asistencias.
    - Público u otros niveles: permite buscar por DNI (?dni=).
    """
    dni = (request.GET.get('dni') or '').strip()
    alumno = None

    if request.user.is_authenticated and getattr(request.user, 'nivel', 1) == 1:
        alumno = request.user
    else:
        if dni:
            alumno = User.objects.filter(dni=dni).first()

    if not alumno:
        if dni and not request.user.is_authenticated:
            messages.error(request, "No se encontró un usuario con ese DNI.")
        return render(request, 'asistencias/consultas.html', {
            'dni': dni, 'alumno': None, 'asistencias': []
        })

    asistencias = (Asistencia.objects
                   .filter(user=alumno)
                   .select_related('clase', 'clase__materia', 'clase__materia__diplomatura')
                   .order_by('-timestamp'))

    return render(request, 'asistencias/consultas.html', {
        'dni': dni, 'alumno': alumno, 'asistencias': asistencias
    })
