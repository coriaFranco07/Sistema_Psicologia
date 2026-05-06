from django.http import Http404
import logging
from django.views.generic import ListView
from apps.core.utils import log_error
from apps.datos_personales.models import DatosPersonales

logger = logging.getLogger(__name__)

class DatosPersonalesListView(ListView):
    model = DatosPersonales
    template_name = "lista_datos_pers.html"
    context_object_name = "usuardatos_pers"

    def get_queryset(self):
        try:
            usuario_pk = self.kwargs['pk']
            return DatosPersonales.objects.filter(username_id=usuario_pk)
        except KeyError:
            logger.error("No se proporcionó 'pk' en la URL.")
            log_error(
                mensaje="Error No se proporcionó 'pk' en la URL"
            )
            raise Http404("Usuario no especificado")
        except (ValueError, TypeError) as e:
            logger.error("Valor de 'pk' inválido: %s", e)
            log_error(
                mensaje=f"Valor de 'pk' inválido: {e}"
            )
            raise Http404("Usuario no válido")
        except Exception as e:
            logger.exception("Error inesperado al obtener datos personales: %s", e)
            log_error(
                mensaje=f"Error inesperado al obtener datos personales: {e}"
            )
            raise Http404("Error al cargar los datos del usuario")