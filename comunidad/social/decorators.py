# decorators.py

from django.core.exceptions import PermissionDenied

def permiso_requerido(permiso):
    def decorator(view_func):
        def wrapped_view(request, *args, **kwargs):
            if request.user.perfilusuario.rol.permisos.filter(codename=permiso).exists():
                return view_func(request, *args, **kwargs)
            else:
                raise PermissionDenied
        return wrapped_view
    return decorator