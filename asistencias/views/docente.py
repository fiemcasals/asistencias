from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponseForbidden
from asistencias.models import Diplomatura, Materia, Clase, InscripcionMateria, ProfesorMateria, Asistencia
from asistencias.permissions import requiere_nivel
from asistencias.forms import CrearMateriaForm
from asistencias.models import ProfesorMateria
from django.db.models import Prefetch



@requiere_nivel(2)
def crear_materia(request):
    if request.method == "POST":
        form = CrearMateriaForm(request.POST)
        if form.is_valid():
            mat = form.save(commit=False)
            mat.profesor_titular = request.user
            mat.save()
            ProfesorMateria.objects.get_or_create(
                user=request.user, materia=mat, rol="titular"
            )
            messages.success(request, "Materia creada.")
            return redirect("asistencias:listar_materias")
    else:
        form = CrearMateriaForm()
    return render(request, "asistencias/crear_materia.html", {"form": form})



@requiere_nivel(2)
def crear_clase(request, materia_id):
    materia = get_object_or_404(Materia, id=materia_id)
    if not ProfesorMateria.objects.filter(user=request.user, materia=materia).exists():
        return HttpResponseForbidden("No sos profesor de esta materia.")
    if request.method == 'POST':
        fecha = request.POST.get('fecha')       # YYYY-MM-DD
        hi = request.POST.get('hora_inicio')    # HH:MM
        hf = request.POST.get('hora_fin')       # HH:MM
        Clase.objects.create(materia=materia, fecha=fecha, hora_inicio=hi, hora_fin=hf)
        messages.success(request, "Clase creada.")
        return redirect('asistencias:ver_clases', materia_id=materia.id)
    return render(request, 'asistencias/crear_clase.html', {'materia': materia})



@requiere_nivel(2)
def listado_presentes(request, materia_id):
    materia = get_object_or_404(Materia.objects.select_related('diplomatura'), id=materia_id)

    # Solo docentes (titular o adjunto) de esta materia
    if not ProfesorMateria.objects.filter(user=request.user, materia=materia).exists():
        return HttpResponseForbidden("No sos profesor de esta materia.")

    # Inscritos con user prefetch
    inscriptos = (InscripcionMateria.objects
                  .filter(materia=materia)
                  .select_related('user')
                  .order_by('user__last_name', 'user__first_name'))

    # Prefetch asistencias por clase para no hacer N+1
    clases = (materia.clases
              .all()
              .prefetch_related(
                  Prefetch('asistencias',
                           queryset=Asistencia.objects.select_related('user').only('user_id', 'presente', 'timestamp'))
              )
              .order_by('-fecha', '-hora_inicio'))

    # Armamos “filas” por clase: cada fila = un alumno inscrito + su asistencia (si existe)
    planillas = []  # [(clase, [filas])]
    for clase in clases:
        # Map rápido user_id -> asistencia
        a_por_uid = {a.user_id: a for a in clase.asistencias.all()}

        filas = []
        for ins in inscriptos:
            u = ins.user
            a = a_por_uid.get(u.id)  # puede ser None
            filas.append({
                'dni': u.dni,
                'alumno': f"{u.last_name}, {u.first_name}",
                'presente': (a.presente if a else False),
                'timestamp': (a.timestamp if a else None),
            })
        planillas.append((clase, filas))

    return render(request, 'asistencias/listado_presentes.html', {
        'materia': materia,
        'planillas': planillas,
    })


# asistencias/views/docentes.py (o donde la tengas)
from django.http import HttpResponseForbidden
from asistencias.models import AccesoToken, Materia

@requiere_nivel(2)
def generar_token_adjunto(request, materia_id):
    materia = get_object_or_404(Materia, id=materia_id)
    if materia.profesor_titular_id != request.user.id:
        return HttpResponseForbidden("Sólo el titular puede generar este token.")

    tok = AccesoToken.objects.create(
        nivel_destino=2,
        materia=materia,
        creado_por=request.user,
    )
    messages.success(request, f"Token generado: {tok.code}")
    return redirect('asistencias:listado_presentes', materia_id=materia.id)
