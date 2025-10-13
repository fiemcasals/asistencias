# asistencias/permissions.py
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required

def requiere_nivel(min_nivel):
    def decorator(view):
        @login_required
        def _wrapped(request, *args, **kwargs):
            if request.user.nivel >= min_nivel:
                return view(request, *args, **kwargs)
            return HttpResponseForbidden("No tenés permisos.")
        return _wrapped
    return decorator
