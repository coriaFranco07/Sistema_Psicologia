from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied
from functools import wraps

from apps.core.utils import log_error
from .models import PermisoModulo, Modulo


def permiso_requerido(modulo_codigo, permiso):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            user = request.user

            if not user.is_authenticated:
                return redirect('login')

            if user.is_superuser or user.is_staff or getattr(user, 'es_admin_local', False):
                return view_func(request, *args, **kwargs)

            try:
                modulo = Modulo.objects.get(codigo=modulo_codigo)
                permiso_modulo = PermisoModulo.objects.get(usuario=user, modulo=modulo)

                if not hasattr(permiso_modulo, permiso):
                    raise PermissionDenied("Permiso inválido.")

                if getattr(permiso_modulo, permiso):
                    return view_func(request, *args, **kwargs)

                raise PermissionDenied("No tenés permiso para acceder a este módulo.")

            except (Modulo.DoesNotExist, PermisoModulo.DoesNotExist):
                log_error(
                    request=request,
                    mensaje="No tenés permiso para acceder a este módulo"
                )
                raise PermissionDenied("No tenés permiso para acceder a este módulo.")

            except Exception:
                log_error(
                    request=request,
                    mensaje="Error verificando permisos"
                )
                raise PermissionDenied("Error verificando permisos.")

        return _wrapped_view
    return decorator


def es_admin_local_o_staff(user):
    if not user.is_authenticated:
        return False
    return user.is_staff or getattr(user, 'es_admin_local', False)