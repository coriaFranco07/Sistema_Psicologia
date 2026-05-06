from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from apps.core.utils import log_error
from apps.permiso.models import Modulo, PermisoModulo
import logging

logger = logging.getLogger(__name__)

class PermisoModuloRequiredMixin:
    modulo_codigo = None
    permiso = None

    def dispatch(self, request, *args, **kwargs):
        user = request.user

        if not user.is_authenticated:
            return redirect('login')

        if user.is_superuser or user.is_staff or getattr(user, 'es_admin_local', False):
            return super().dispatch(request, *args, **kwargs)

        if not self.modulo_codigo or not self.permiso:
            raise PermissionDenied("Configuración de permisos incompleta.")

        try:
            modulo = Modulo.objects.get(codigo=self.modulo_codigo)
            permiso_modulo = PermisoModulo.objects.get(usuario=user, modulo=modulo)

            if not hasattr(permiso_modulo, self.permiso):
                raise PermissionDenied("Permiso inválido.")

            if getattr(permiso_modulo, self.permiso):
                return super().dispatch(request, *args, **kwargs)

            raise PermissionDenied("No tenés permiso para acceder a este módulo.")

        except Modulo.DoesNotExist:
            log_error(
                request=request,
                mensaje="1. Error No tenés permiso para acceder a este módulo"
            )
            raise PermissionDenied("No tenés permiso para acceder a este módulo.")
        except PermisoModulo.DoesNotExist:
            log_error(
                request=request,
                mensaje="2. Error No tenés permiso para acceder a este módulo"
            )
            raise PermissionDenied("No tenés permiso para acceder a este módulo.")
        except PermisoModulo.MultipleObjectsReturned:
            logger.error("Permisos duplicados: usuario_id=%s, módulo=%s", user.id, self.modulo_codigo)
            log_error(
                request=request,
                mensaje=f"Error Permisos duplicados: usuario_id={user.id}, módulo={self.modulo_codigo}"
            )
            raise PermissionDenied("Error de configuración: permisos duplicados")
        except Exception as e:
            logger.exception("Error verificando permisos: %s", str(e))
            log_error(
                request=request,
                mensaje=f"Error verificando permisos: {str(e)}"
            )
            raise PermissionDenied("Error verificando permisos.")


