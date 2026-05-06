from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.contrib import messages
from apps.core.utils import log_error
from apps.permiso.forms import ModuloForm
from apps.permiso.models import PermisoModulo, Modulo
from apps.usuario.models import Usuario
from apps.permiso.decorators import permiso_requerido
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, ListView
import logging
from django.core.exceptions import PermissionDenied

logger = logging.getLogger(__name__)

class ModuloListView(ListView):
    model = Modulo
    template_name = "modulo/modulo_list.html"
    context_object_name = "modulos"
    ordering = ['nombre']

class ModuloCreateView(CreateView):
    model = Modulo
    form_class = ModuloForm
    template_name = "modulo/modulo_form.html"
    success_url = reverse_lazy("permiso:lista_modulo")
    context_object_name = "modulo"

class ModuloEditView(UpdateView):
    model = Modulo
    form_class = ModuloForm  
    template_name = "modulo/modulo_form.html"
    success_url = reverse_lazy("permiso:lista_modulo")
    context_object_name = "modulo"
    

@login_required
def gestionar_permisos(request):

    if not request.user.is_staff:
        raise PermissionDenied(
            "No tenés permiso para acceder a este módulo."
        )
    
    usuarios = Usuario.objects.order_by('username')
    modulos = Modulo.objects.filter(activo=True).order_by('nombre')

    # ✅ Validar usuario_id
    usuario_id = request.GET.get('usuario_id')
    try:
        usuario_id = int(usuario_id) if usuario_id else None
        logger.debug("Filtro usuario_id: %s", usuario_id)
    except ValueError:
        usuario_id = None
        log_error(
            request=request,
            mensaje=f"Error usuario_id inválido recibido en GET: {request.GET.get('usuario_id')}"
        )
        logger.warning("usuario_id inválido recibido en GET: %s", request.GET.get('usuario_id'))

    permisos = PermisoModulo.objects.select_related('usuario', 'modulo') \
                .order_by('usuario__username', 'modulo__nombre')

    if usuario_id:
        permisos = permisos.filter(usuario_id=usuario_id)

    if request.method == 'POST':
        action = request.POST.get('action')
        logger.info("POST action recibida: %s", action)

        if action == 'toggle_permiso':
            try:
                permiso_id = request.POST.get('permiso_id')
                field = request.POST.get('field')
                value = request.POST.get('value') == 'true'

                logger.debug("Toggle permiso_id=%s, field=%s, value=%s", permiso_id, field, value)

                if not permiso_id:
                    logger.warning("permiso_id no recibido en toggle_permiso")
                    return JsonResponse({'success': False, 'message': 'ID inválido'})

                if field not in ['puede_ver','puede_editar','puede_eliminar','puede_agregar']:
                    logger.warning("Campo no válido en toggle_permiso: %s", field)
                    return JsonResponse({'success': False, 'message': 'Campo no válido'})

                permiso = get_object_or_404(PermisoModulo, id=permiso_id)

                setattr(permiso, field, value)
                permiso.save(update_fields=[field])

                logger.info("Permiso actualizado: id=%s, %s=%s", permiso.id, field, value)
                return JsonResponse({'success': True})

            except Exception as e:
                logger.exception("Error toggle permiso: %s", e)
                log_error(
                    request=request,
                    mensaje=f"Error toggle permiso: {e}"
                )
                return JsonResponse({'success': False, 'message': 'Error interno'})

        elif action == 'agregar_modulo':
            usuario_id_post = request.POST.get('usuario_select')
            modulo_id = request.POST.get('modulo_select')
            logger.debug("Agregar modulo: usuario_id=%s, modulo_id=%s", usuario_id_post, modulo_id)

            if not usuario_id_post or not modulo_id:
                messages.error(request, "Debe seleccionar un usuario y un módulo.")
                logger.warning("No se recibieron usuario o modulo en agregar_modulo")
                return redirect(request.path)

            usuario = get_object_or_404(Usuario, id=usuario_id_post)
            modulo = get_object_or_404(Modulo, id=modulo_id)

            try:
                permiso, created = PermisoModulo.objects.get_or_create(usuario=usuario, modulo=modulo)
                if created:
                    permiso.puede_ver = False
                    permiso.puede_editar = False
                    permiso.puede_eliminar = False
                    permiso.puede_agregar = False
                    permiso.save()
                    logger.info("Módulo '%s' asignado a usuario '%s'", modulo.nombre, usuario.username)
                    messages.success(request, f"Módulo '{modulo.nombre}' asignado a '{usuario.username}'.")
                else:
                    logger.info("Módulo '%s' ya estaba asignado a usuario '%s'", modulo.nombre, usuario.username)
                    messages.warning(request, f"El módulo '{modulo.nombre}' ya está asignado a '{usuario.username}'.")

            except Exception as e:
                logger.exception("Error asignando módulo: %s", e)
                log_error(
                    request=request,
                    mensaje=f"Error asignando módulo: {e}"
                )
                messages.error(request, "Error asignando el módulo.")
                return redirect(request.path)

            return redirect(f"{request.path}?usuario_id={usuario.id}")

    return render(request, 'permiso/gestionar_permisos.html', {
        'usuarios': usuarios,
        'modulos': modulos,
        'permisos': permisos,
        'usuario_id': usuario_id,
    })
