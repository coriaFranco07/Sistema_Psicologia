from django.utils import timezone
import json
from apps.parametros.models import Parametros
from django.db import DatabaseError
import logging
import traceback
import inspect
from django.core.exceptions import ObjectDoesNotExist

logger = logging.getLogger(__name__)


def log_error(usuario=None, request=None, mensaje="", nivel="ERROR"):
    try:
        from apps.core.models import LogSistema
        # ruta automática
        frame = inspect.stack()[1]
        ruta = f"{frame.filename} -> {frame.function}"

        usuario_final = None

        if getattr(usuario, "is_authenticated", False):
            usuario_final = usuario

        elif getattr(request, "user", None) and getattr(request.user, "is_authenticated", False):
            usuario_final = request.user


        metodo_http = request.method if request else None
        url = request.path if request else None
        ip = request.META.get("REMOTE_ADDR") if request else None

        detalle = traceback.format_exc()
        if detalle == "NoneType: None\n":
            detalle = None

        LogSistema.objects.create(
            usuario=usuario_final,
            fecha_hora=timezone.now(),
            nivel=nivel,
            mensaje=mensaje,
            detalle=detalle,
            ruta=ruta,
            metodo_http=metodo_http,
            url=url,
            ip_cliente=ip,
            modulo=frame.filename.split("/")[-2] if "/" in frame.filename else None
        )

    except Exception as e:
        print("❌ Error guardando log:", e)


def get_parametro_json(nombre):
    """Obtiene el valor JSON de un parámetro por nombre."""
    try:
        parametro = Parametros.objects.get(nombre_parametro=nombre)
        if parametro.valor_parametro is None:
            return None
        return json.loads(parametro.valor_parametro)
    except Parametros.DoesNotExist:
        logger.warning("Parámetro no encontrado: %s", nombre)
        return None
    except json.JSONDecodeError as e:
        logger.error("JSON inválido para parámetro %s: %s\n%s", nombre, e, traceback.format_exc())
        return None
    except DatabaseError as e:
        logger.error("Error de base de datos al obtener parámetro %s: %s\n%s", nombre, e, traceback.format_exc())
        return None
    except Exception as e:
        logger.error("Error inesperado en get_parametro_json para %s: %s\n%s", nombre, e, traceback.format_exc())
        return None


def user_estado(user):
    from apps.usuario.models import Usuario
    """Retorna True si el usuario tiene servicio activo, False en otro caso."""
    estado = True
    try:
        socio_estado = Usuario.objects.get(username=user)
        if not socio_estado.id_std_socio or not socio_estado.id_std_socio.servicio:
            estado = False
    except ObjectDoesNotExist:
        logger.warning("Usuario no encontrado en user_estado: %s", user)
        estado = False
    except Exception as e:
        logger.error("Error inesperado en user_estado para %s: %s\n%s", user, e, traceback.format_exc())
        estado = False
    return estado


def user_estado_control(user):
    from apps.usuario.models import Usuario
    """Retorna True si el usuario no está bloqueado y tiene estado asignado."""
    estado = True
    try:
        socio_estado = Usuario.objects.get(username=user)
        if not socio_estado.id_std_socio or socio_estado.id_std_socio.bloqueado:
            estado = False
    except ObjectDoesNotExist:
        logger.warning("Usuario no encontrado en user_estado_control: %s", user)
        estado = False
    except Exception as e:
        logger.error("Error inesperado en user_estado_control para %s: %s\n%s", user, e, traceback.format_exc())
        estado = False
    return estado


import ipaddress

def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")

    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0].strip()
    else:
        ip = request.META.get("REMOTE_ADDR")

    try:
        ipaddress.ip_address(ip)
        return ip
    except:
        return "0.0.0.0"