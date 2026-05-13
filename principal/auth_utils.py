from apps.usuario.models import Paciente, Psicologo


def _estado_es_inactivo(estado):
    return bool(estado and (estado.dsc_estado or "").strip().upper() == "INACTIVO")


def _normalize_username(username):
    if username is None:
        return ""
    return str(username).strip()


def get_profile_role_for_username(username):
    username = _normalize_username(username)
    if not username or not username.isdigit():
        return None

    if Psicologo.objects.filter(dni=username).exists():
        return "psicologo"

    if Paciente.objects.filter(dni=username).exists():
        return "paciente"

    return None


def get_panel_role_for_user(user):
    if not getattr(user, "is_authenticated", False):
        return "anonymous"

    if user.is_staff or user.is_superuser:
        return "admin"

    return get_profile_role_for_username(getattr(user, "username", None)) or "usuario"


def get_inactive_profile_for_username(username):
    username = _normalize_username(username)
    if not username or not username.isdigit():
        return None

    psicologo = (
        Psicologo.objects.select_related("id_estado").filter(dni=username).first()
    )
    if psicologo and _estado_es_inactivo(psicologo.id_estado):
        return psicologo

    paciente = Paciente.objects.select_related("id_estado").filter(dni=username).first()
    if paciente and _estado_es_inactivo(paciente.id_estado):
        return paciente

    return None


def user_has_inactive_profile(user):
    return get_inactive_profile_for_username(getattr(user, "username", None)) is not None
