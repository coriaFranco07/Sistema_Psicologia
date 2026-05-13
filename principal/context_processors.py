from .auth_utils import get_panel_role_for_user


def panel_context(request):
    return {
        "panel_role": get_panel_role_for_user(getattr(request, "user", None)),
    }
