import os
from urllib import request
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from apps.core.utils import log_error
from apps.permiso.permissionmixin import PermisoModuloRequiredMixin
from django.urls import reverse
from django.shortcuts import render, redirect
from .forms import UsuarioForm, DatosPersonalesForm, UsuarioUpdateForm
from .models import Usuario
from apps.datos_personales.models import DatosPersonales
from django.views.generic import CreateView, UpdateView, ListView
from django.urls import reverse_lazy
from datetime import date, datetime
from django.db import transaction
import logging
from django.core.exceptions import ObjectDoesNotExist

logger = logging.getLogger(__name__)

class UsuarioListView(PermisoModuloRequiredMixin, ListView):

    model = Usuario
    modulo_codigo = 'usuarios'
    permiso = 'puede_ver'

    template_name = "lista_usuarios.html"


class UsuarioUpdateView(PermisoModuloRequiredMixin, UpdateView):
    model = Usuario
    modulo_codigo = 'usuarios'
    permiso = 'puede_editar'
    form_class = UsuarioUpdateForm
    template_name = "editar_usuario.html"
    success_url = reverse_lazy("usuario:usuarios_list")

    def get_object(self):
        return super().get_object()

    def get_datos_instance(self):
        usuario = self.get_object()
        datos = usuario.usuario_datos.first()
        if not datos:
            datos = DatosPersonales(username=usuario)
        return datos

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        usuario = self.object
        datos = self.get_datos_instance()

        form = UsuarioUpdateForm(instance=usuario, is_edit=True)
        datos_form = DatosPersonalesForm(instance=datos, is_edit=True)

        return render(request, self.template_name, {
            "form": form,
            "datos_form": datos_form
        })

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        usuario = self.object
        datos = self.get_datos_instance()

        form = UsuarioUpdateForm(
            request.POST,
            instance=usuario,
            is_edit=True
        )

        datos_form = DatosPersonalesForm(
            request.POST,
            instance=datos,
            is_edit=True
        )

        if form.is_valid() and datos_form.is_valid():
            with transaction.atomic():
                form.save()
                datos_personales = datos_form.save(commit=False)
                datos_personales.username = usuario
                datos_personales.save()

            messages.success(request, "Usuario actualizado correctamente.")
            return redirect(self.success_url)

        # SI FALLA, vuelve con datos y errores
        return render(request, self.template_name, {
            "form": form,
            "datos_form": datos_form
        })


class UsuarioCreateView(PermisoModuloRequiredMixin, CreateView):
    model = Usuario
    modulo_codigo = 'usuarios'
    permiso = 'puede_agregar'
    form_class = UsuarioForm
    template_name = "registrar_usuario.html"
    success_url = reverse_lazy("usuario:usuarios_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["datos_form"] = DatosPersonalesForm(self.request.POST)
        else:
            context["datos_form"] = DatosPersonalesForm()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        datos_form = context["datos_form"]

        if datos_form.is_valid():
            tipo_socio = form.cleaned_data["id_tipo_socio"]

            if tipo_socio.relacion:
                # Guardar en sesión
                usuario_data = {}

                for k, v in form.cleaned_data.items():
                    if hasattr(v, "pk"):
                        # Guardar tanto el formato con _id como el directo
                        usuario_data[k + "_id"] = v.pk
                        usuario_data[k] = v.pk  # También guardar el formato directo para compatibilidad
                    elif isinstance(v, date):
                        usuario_data[k] = v.isoformat()
                    else:
                        usuario_data[k] = v

                datos_personales_data = {}
                for k, v in datos_form.cleaned_data.items():
                    if isinstance(v, date):
                        datos_personales_data[k] = v.isoformat()
                    elif hasattr(v, 'pk'):
                        datos_personales_data[k + "_id"] = v.pk
                        datos_personales_data[k] = v.pk  # También guardar el formato directo
                    else:
                        datos_personales_data[k] = v

                self.request.session['usuario_data'] = usuario_data
                self.request.session['datos_personales_data'] = datos_personales_data

                return redirect(reverse('usuario:completar_relacion'))

            else:
                try:
                    # Guardar directamente si no requiere relación
                    with transaction.atomic():

                        usuario = form.save(commit=False)
                        usuario.set_password(form.cleaned_data["password1"])

                        print("\n===== DATOS USUARIO =====")
                        for k, v in form.cleaned_data.items():
                            print(f"{k}: {v}")
                        print("=========================\n")


                        usuario.save()

                        # Capturar fecha_socio_alta si existe, sino usar date.today()
                        fecha_socio_alta_str = self.request.POST.get("fecha_socio_alta")

                        if fecha_socio_alta_str:
                            try:
                                fecha_socio_alta = datetime.strptime(fecha_socio_alta_str, "%Y-%m-%d").date()
                            except ValueError:
                                messages.error(request, "Formato de fecha inválido.")
                                return self.form_invalid(form)
                        else:
                            fecha_socio_alta = date.today()
                        
                        datos_personales = datos_form.save(commit=False)
                        datos_personales.username = usuario

                        print("\n===== DATOS PERSONALES =====")
                        for k, v in datos_form.cleaned_data.items():
                            print(f"{k}: {v}")
                        print("============================\n")


                        datos_personales.save()


                except Exception:
                    logger.exception("Error creando usuario")
                    log_error(
                        usuario=self.request.user,
                        request=self.request,
                        mensaje="Error creando usuario"
                    )
                    messages.error(request, "Error inesperado al crear el usuario.")
                    return self.form_invalid(form)

                return redirect(self.success_url)
        else:
            return self.form_invalid(form)

