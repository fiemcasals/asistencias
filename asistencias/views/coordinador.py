from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from asistencias.models import Diplomatura
from asistencias.permissions import requiere_nivel


@requiere_nivel(3)
def crear_diplomatura(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        codigo = request.POST.get('codigo', '').strip()
        Diplomatura.objects.create(nombre=nombre, codigo=codigo, creada_por=request.user)
        messages.success(request, "Diplomatura creada.")
        return redirect('asistencias:listar_diplomaturas')
    return render(request, 'asistencias/crear_diplomatura.html')


@requiere_nivel(3)
def cargar_excel_inscripciones(request, diplo_id):
    dip = get_object_or_404(Diplomatura, id=diplo_id)
    if request.method == 'POST' and request.FILES.get('archivo'):
        # TODO: parsear CSV/XLSX aquí
        messages.success(request, "Carga procesada (demo).")
        return redirect('asistencias:listar_diplomaturas')
    return render(request, 'asistencias/cargar_excel.html', {'diplomatura': dip})
