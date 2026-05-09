from datetime import timezone
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth import authenticate
from django.core.signing import TimestampSigner
import json
from apps.core.utils import get_parametro_json, log_error, user_estado_control
from apps.datos_personales.models import DatosPersonales
from apps.datos_personales.serializers import DatosPersonalesSerializer
import logging
import traceback

logger = logging.getLogger(__name__)
MOBILE_AUTH_SALT = "mobile-mercadopago-auth"


def build_absolute_media_url(request, relative_url):
    if not relative_url:
        return relative_url
    return request.build_absolute_uri(relative_url)

@csrf_exempt
def login(request):
    try:

        if request.method != 'POST':
            return JsonResponse({"error": "Método no permitido"}, status=405)

        try:
            data = json.loads(request.body.decode('utf-8') or "{}")
        except json.JSONDecodeError:
            log_error(
                    request=request,
                    mensaje="Error JSON inválido"
            )
            return JsonResponse({"error": "JSON inválido"}, status=400)

        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return JsonResponse({"error": "Faltan credenciales"}, status=400)

        user = authenticate(request, username=username, password=password)
        if user is None:
            return JsonResponse({"error": "Usuario o contraseña incorrectos"}, status=401)
        mobile_auth_token = TimestampSigner(salt=MOBILE_AUTH_SALT).sign(str(user.id))


        # Datos básicos del usuario
        datos_usuario = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "dni": user.dni,
            "nombres": getattr(user, 'nombres', ''),  # por si no tiene campo nombres
            "foto_url": build_absolute_media_url(request, user.foto_url)
        }

        # 👇 Traer datos personales asociados
        try:
            datos_personales_obj = DatosPersonales.objects.get(username_id=user.id)
            serializer = DatosPersonalesSerializer(datos_personales_obj)
            datos_personales = serializer.data
        except DatosPersonales.DoesNotExist:
            datos_personales = {}  # si no existen datos personales

        
        return JsonResponse({
            "user_id": user.id,
            "username": user.username,
            "mobile_auth_token": mobile_auth_token,
            "datos_usuario": datos_usuario,
            "datos_personales": datos_personales  # aquí están los datos completos
        })
    
    except Exception as e:
        logger.error("Error inesperado en login: %s\n%s", e, traceback.format_exc())
        log_error(
                request=request,
                mensaje=f"Error inesperado en login: {e}"
        )
        return JsonResponse({"error": "Ocurrió un error inesperado"}, status=500)





