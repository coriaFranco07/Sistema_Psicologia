from django import template
from apps.permiso.models import PermisoModulo, Modulo

register = template.Library()

@register.simple_tag
def tiene_permiso(user, modulo_codigo, permiso):
    if not user.is_authenticated:
        return False

    # Admins pasan siempre
    if user.is_superuser or user.is_staff or getattr(user, 'es_admin_local', False):
        return True

    try:
        modulo = Modulo.objects.get(codigo=modulo_codigo)
        permiso_modulo = PermisoModulo.objects.get(usuario=user, modulo=modulo)
        return getattr(permiso_modulo, permiso, False)
    except (Modulo.DoesNotExist, PermisoModulo.DoesNotExist):
        return False