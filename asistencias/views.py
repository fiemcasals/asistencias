from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponse
from .models import Diplomatura, Materia, Clase, Asistencia, Alumno
from .forms import DiplomaturaForm, MateriaForm, ClaseForm, MarcarPresenteForm

# PDF
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm

def home(request):
    diplomaturas = Diplomatura.objects.all().order_by('nombre')
    return render(request, 'asistencias/home.html', {'diplomaturas': diplomaturas})

def publico(request):
    # lista de clases habilitadas ahora mismo
    ahora = timezone.now()
    #select_related para optimizar consultas, traer diplomatura y materia en la misma consulta
    #las ordena por diplomatura, materia y fecha
    clases = Clase.objects.filter(inicio_habilitacion__lte=ahora, 
    fin_habilitacion__gte=ahora).select_related('materia', 'materia__diplomatura').order_by('materia__diplomatura__nombre','materia__nombre','fecha')
    return render(request, 'asistencias/publico.html', {'clases': clases})#apunta a un html

def marcar_presente(request, clase_id):
    clase = get_object_or_404(Clase, pk=clase_id)
    if not clase.esta_habilitada():
        messages.error(request, 'La ventana de asistencia no está activa para esta clase.')
        return redirect('asistencias:publico')#va a una url con name 'publico' en urls.py y luego a la view publico

    if request.method == 'POST':
        form = MarcarPresenteForm(request.POST)
        if form.is_valid():
            dni = form.cleaned_data['dni']#levanta el dni del form y limpia el campo 
            try:
                alumno = Alumno.objects.get(dni=dni)
            except Alumno.DoesNotExist:
                messages.error(request, 'DNI no encontrado. Consulte con el docente.')
                return redirect('asistencias:publico')

            obj, created = Asistencia.objects.get_or_create(clase=clase, alumno=alumno, defaults={'presente': True})# el obj es el objeto creado o existente, created es booleano, representando si se creo o no
            if created:
                messages.success(request, f'¡Presente registrado para {alumno}!')
            else:
                if not obj.presente:
                    obj.presente = True
                    obj.save()
                messages.info(request, 'Ya estabas marcado como presente para esta clase.')
            return redirect('asistencias:publico')
    else:
        form = MarcarPresenteForm()
    return render(request, 'asistencias/marcar_presente.html', {'clase': clase, 'form': form})

def consulta_asistencias(request):
    # consulta por DNI (público)
    dni = request.GET.get('dni', '').strip()
    asistencias = None
    alumno = None
    if dni:
        try:
            alumno = Alumno.objects.get(dni=dni)
            asistencias = alumno.asistencias.select_related('clase','clase__materia','clase__materia__diplomatura').order_by('-clase__fecha')
        except Alumno.DoesNotExist:
            messages.error(request, 'DNI no encontrado.')
    return render(request, 'asistencias/consulta.html', {'dni': dni, 'alumno': alumno, 'asistencias': asistencias})

@login_required
def gestion(request):
    diplomaturas = Diplomatura.objects.all()
    materias = Materia.objects.select_related('diplomatura').all()
    return render(request, 'asistencias/gestion.html', {'diplomaturas': diplomaturas, 'materias': materias})

@login_required
def diplomatura_nueva(request):
    if request.method == 'POST':
        form = DiplomaturaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Diplomatura creada.')
            return redirect('asistencias:gestion')
    else:
        form = DiplomaturaForm()
    return render(request, 'asistencias/form.html', {'form': form, 'titulo': 'Nueva Diplomatura'})

@login_required
def materia_nueva(request):
    if request.method == 'POST':
        form = MateriaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Materia creada.')
            return redirect('asistencias:gestion')
    else:
        form = MateriaForm()
    return render(request, 'asistencias/form.html', {'form': form, 'titulo': 'Nueva Materia'})

@login_required
def clase_nueva(request):
    if request.method == 'POST':
        form = ClaseForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Clase creada.')
            return redirect('asistencias:gestion')
    else:
        form = ClaseForm()
    return render(request, 'asistencias/form.html', {'form': form, 'titulo': 'Nueva Clase'})

@login_required
def listado_clases(request, materia_id):
    materia = get_object_or_404(Materia, pk=materia_id)
    clases = materia.clases.order_by('-fecha')
    # listado combinado de asistencias por clase
    return render(request, 'asistencias/listado_clases.html', {'materia': materia, 'clases': clases})

@login_required
def exportar_asistencias_pdf(request, materia_id):
    materia = get_object_or_404(Materia, pk=materia_id)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="asistencias_{materia.id}.pdf"'
    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    margin = 2*cm
    x = margin
    y = height - margin
    p.setFont("Helvetica-Bold", 14)
    p.drawString(x, y, f"Asistencias - {materia.nombre} / {materia.diplomatura.nombre}")
    y -= 1.0*cm
    p.setFont("Helvetica", 10)

    for clase in materia.clases.order_by('fecha'):
        if y < 3*cm:
            p.showPage()
            y = height - margin
            p.setFont("Helvetica-Bold", 14)
            p.drawString(x, y, f"Asistencias - {materia.nombre} / {materia.diplomatura.nombre}")
            y -= 1.0*cm
            p.setFont("Helvetica", 10)

        p.setFont("Helvetica-Bold", 11)
        p.drawString(x, y, f"Clase: {clase.fecha} - {clase.tema or ''}")
        y -= 0.5*cm
        p.setFont("Helvetica", 10)
        # encabezados
        p.drawString(x, y, "DNI")
        p.drawString(x+4*cm, y, "Apellido, Nombre")
        p.drawString(x+11*cm, y, "Presente")
        y -= 0.4*cm

        for a in clase.asistencias.select_related('alumno').order_by('alumno__apellido1', 'alumno__nombre1'):
            nombre = f"{a.alumno.apellido1}, {a.alumno.nombre1}"
            p.drawString(x, y, a.alumno.dni)
            p.drawString(x+4*cm, y, nombre[:40])
            p.drawString(x+11*cm, y, "Sí" if a.presente else "No")
            y -= 0.35*cm
            if y < 2.5*cm:
                p.showPage()
                y = height - margin
                p.setFont("Helvetica-Bold", 14)
                p.drawString(x, y, f"Asistencias - {materia.nombre} / {materia.diplomatura.nombre}")
                y -= 1.0*cm
                p.setFont("Helvetica", 10)

    p.showPage()
    p.save()
    return response
