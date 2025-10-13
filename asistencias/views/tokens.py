# asistencias/views/tokens.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from asistencias.models import AccesoToken, ProfesorMateria
from asistencias.permissions import requiere_nivel
 



@requiere_nivel(1)
def usar_token(request):
    if request.method == 'POST':
        code = request.POST.get('code', '').strip()
        tok = get_object_or_404(AccesoToken, code=code)

        if not tok.es_valido():
            messages.error(request, "Token inválido/expirado/ya usado.")
            return redirect('asistencias:home')

        # subir nivel si corresponde
        if request.user.nivel < tok.nivel_destino:
            request.user.nivel = tok.nivel_destino
            request.user.save()

        # si el token apunta a una materia, asociar como adjunto
        if tok.materia_id:
            ProfesorMateria.objects.get_or_create(
                user=request.user, materia=tok.materia, defaults={'rol': 'adjunto'}
            )

        tok.usado_por = request.user
        tok.usado_en = timezone.now()
        tok.save()

        messages.success(request, "Token aplicado.")
        return redirect('asistencias:home')

    return render(request, 'asistencias/usar_token.html')
