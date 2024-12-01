# decorators.py

from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect
from django.conf import settings

def requires_login_or_404(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(settings.LOGIN_URL)
        return view_func(request, *args, **kwargs)
    return wrapper

def permiso_requerido(permiso):
    def decorator(view_func):
        def wrapped_view(request, *args, **kwargs):
            if request.user.perfilusuario.rol.permisos.filter(codename=permiso).exists():
                return view_func(request, *args, **kwargs)
            else:
                raise PermissionDenied
        return wrapped_view
    return decorator
