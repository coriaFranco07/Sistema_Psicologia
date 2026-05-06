from django.shortcuts import render
from apps.core.utils import log_error
from apps.permiso.decorators import permiso_requerido
from django.db import transaction
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import logging

logger = logging.getLogger(__name__)

@login_required
@permiso_requerido('contraseñas', 'puede_editar')
def resetear_password_usuario(request):
    from apps.usuario.forms import ResetPasswordUsuarioForm
    """
    Permite resetear la contraseña de un usuario seleccionado.
    Maneja errores y registra logs de cualquier excepción.
    """
    try:
        if request.method == "POST":
            form = ResetPasswordUsuarioForm(request.POST)

            if form.is_valid():
                usuario = form.cleaned_data.get("usuario")
                nueva_password = form.cleaned_data.get("password1")

                if not usuario:
                    messages.error(request, "No se seleccionó ningún usuario.")
                    return redirect("usuario:reset_password_usuario")

                try:
                    with transaction.atomic():
                        # 🔐 Hash seguro
                        usuario.set_password(nueva_password)
                        usuario.save(update_fields=["password"])
                        messages.success(
                            request,
                            f"Contraseña actualizada correctamente para {usuario.username}"
                        )
                        logger.info(f"Contraseña reseteada para usuario ID={usuario.pk}, username={usuario.username}")
                        return redirect("usuario:reset_password_usuario")
                except Exception as e:
                    logger.exception(f"Error guardando nueva contraseña para usuario ID={usuario.pk}")
                    messages.error(request, "Ocurrió un error al actualizar la contraseña. Intente nuevamente.")

            else:
                messages.error(request, "El formulario contiene errores. Revíselo y vuelva a intentar.")

        else:
            form = ResetPasswordUsuarioForm()

    except Exception as e:
        logger.exception("Error inesperado en resetear_password_usuario")
        log_error(
                usuario=request.user,
                request=request,
                mensaje="Error al resetear_password_usuario"
        )
        messages.error(request, "Ocurrió un error inesperado. Intente nuevamente.")
        form = ResetPasswordUsuarioForm()  # Re-crear formulario para GET

    return render(
        request,
        "usuario/reset_password_usuario.html",
        {"form": form}
    )

