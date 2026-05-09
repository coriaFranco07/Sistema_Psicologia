from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import transaction
from django.db.models import CharField, Q
from django.db.models.functions import Cast
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, DetailView, ListView, TemplateView, UpdateView

from apps.datos_personales.forms import DatosPersonalesForm
from apps.datos_personales.models import DatosPersonales

from .forms import (
    DatosPersonalesSolicitudForm,
    PacienteForm,
    PsicologoForm,
    PsicologoMetodoPagoForm,
    PsicologoOficinaForm,
    PsicologoPendienteForm,
)
from .models import Paciente, Psicologo, PsicologoMetodoPago, PsicologoOficina, PsicologoPendiente


class PsicologoOwnerOrStaffMixin(LoginRequiredMixin, UserPassesTestMixin):
    psicologo_owner_field = "id_psicologo"

    def get_logged_psicologo(self):
        if not self.request.user.is_authenticated:
            return None
        return Psicologo.objects.filter(dni=self.request.user.username).first()

    def user_is_staff(self):
        user = self.request.user
        return user.is_staff or user.is_superuser

    def test_func(self):
        if self.user_is_staff():
            return True
        psicologo = self.get_logged_psicologo()
        if psicologo is None:
            return False
        obj = getattr(self, "object", None)
        if obj is None:
            return True
        return getattr(obj, self.psicologo_owner_field + "_id") == psicologo.pk

    def get_owner_filtered_queryset(self, queryset):
        if self.user_is_staff():
            return queryset
        psicologo = self.get_logged_psicologo()
        if psicologo is None:
            return queryset.none()
        return queryset.filter(**{self.psicologo_owner_field: psicologo})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        kwargs["psicologo"] = self.get_logged_psicologo()
        return kwargs


class DashboardView(TemplateView):
    template_name = "usuario/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_psicologos"] = Psicologo.objects.count()
        context["total_psicologos_pendientes"] = PsicologoPendiente.objects.filter(
            estado=PsicologoPendiente.ESTADO_PENDIENTE
        ).count()
        context["total_pacientes"] = Paciente.objects.count()
        context["ultimos_psicologos"] = Psicologo.objects.select_related(
            "id_estado", "id_rama"
        ).order_by("-fch_creacion")[:5]
        context["ultimos_pacientes"] = Paciente.objects.select_related(
            "id_estado", "id_ocupacion", "id_ciclo_vida"
        ).order_by("-fch_creacion")[:5]
        return context


class PsicologoPendienteListView(ListView):
    model = PsicologoPendiente
    template_name = "psicologo/psicologo_pendiente.html"
    context_object_name = "solicitudes"

    def get_queryset(self):
        queryset = PsicologoPendiente.objects.select_related(
            "id_rama",
            "id_sexo",
            "id_std_civil",
            "id_pais",
            "id_provincia",
            "id_localidad",
            "id_zona",
            "psicologo",
        ).order_by("-fch_creacion")

        estado = self.request.GET.get("estado", "").strip().upper()
        if estado in dict(PsicologoPendiente.ESTADOS):
            queryset = queryset.filter(estado=estado)

        query = self.request.GET.get("q", "").strip()
        if not query:
            return queryset

        return queryset.annotate(
            dni_text=Cast("dni", output_field=CharField()),
            cuil_text=Cast("cuil", output_field=CharField()),
        ).filter(
            Q(nombres__icontains=query)
            | Q(email__icontains=query)
            | Q(dni_text__icontains=query)
            | Q(cuil_text__icontains=query)
            | Q(id_rama__dsc_rama__icontains=query)
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query"] = self.request.GET.get("q", "").strip()
        context["estado"] = self.request.GET.get("estado", "").strip().upper()
        context["estados"] = PsicologoPendiente.ESTADOS
        context["total_resultados"] = self.object_list.count()
        return context


class PsicologoPendienteDetailView(DetailView):
    model = PsicologoPendiente
    template_name = "psicologo/psicologo_pendiente_detail.html"
    context_object_name = "solicitud"

    def get_queryset(self):
        return PsicologoPendiente.objects.select_related(
            "id_rama",
            "id_sexo",
            "id_std_civil",
            "id_pais",
            "id_provincia",
            "id_localidad",
            "id_zona",
            "psicologo",
        )


class PsicologoListView(ListView):
    model = Psicologo
    template_name = "psicologo/psicologo_list.html"
    context_object_name = "psicologos"

    def get_queryset(self):
        queryset = (
            Psicologo.objects.select_related(
                "id_estado",
                "id_rama",
                "datos_personales",
                "datos_personales__id_sexo",
                "datos_personales__id_std_civil",
                "datos_personales__id_pais",
                "datos_personales__id_provincia",
                "datos_personales__id_localidad",
                "datos_personales__id_zona",
            )
            .annotate(
                dni_text=Cast("dni", output_field=CharField()),
                cuil_text=Cast("cuil", output_field=CharField()),
            )
            .order_by("nombres", "dni")
        )

        query = self.request.GET.get("q", "").strip()
        if not query:
            return queryset

        filtros = (
            Q(nombres__icontains=query)
            | Q(email__icontains=query)
            | Q(dni_text__icontains=query)
            | Q(cuil_text__icontains=query)
            | Q(datos_personales__telefono__icontains=query)
            | Q(datos_personales__domicilio__icontains=query)
            | Q(id_estado__dsc_estado__icontains=query)
            | Q(id_rama__dsc_rama__icontains=query)
            | Q(datos_personales__id_sexo__dsc_tipo__icontains=query)
            | Q(datos_personales__id_std_civil__dsc_std_civil__icontains=query)
            | Q(datos_personales__id_pais__dsc_pais__icontains=query)
            | Q(datos_personales__id_provincia__dsc_provincia__icontains=query)
            | Q(datos_personales__id_localidad__dsc_localidad__icontains=query)
            | Q(datos_personales__id_zona__dsc_zona__icontains=query)
        )
        return queryset.filter(filtros)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query"] = self.request.GET.get("q", "").strip()
        context["total_resultados"] = self.object_list.count()
        return context


class PsicologoDetailView(DetailView):
    model = Psicologo
    template_name = "psicologo/psicologo_detail.html"
    context_object_name = "psicologo"

    def get_queryset(self):
        return Psicologo.objects.select_related(
            "id_estado",
            "id_rama",
            "datos_personales",
            "datos_personales__id_sexo",
            "datos_personales__id_std_civil",
            "datos_personales__id_pais",
            "datos_personales__id_provincia",
            "datos_personales__id_localidad",
            "datos_personales__id_zona",
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["datos_personales"] = self.object.datos_personales_rel
        return context


class PacienteListView(ListView):
    model = Paciente
    template_name = "paciente/paciente_list.html"
    context_object_name = "pacientes"

    def get_queryset(self):
        queryset = (
            Paciente.objects.select_related(
                "id_estado",
                "datos_personales",
                "id_ocupacion",
                "id_ciclo_vida",
                "id_grado_estudio",
            )
            .annotate(
                dni_text=Cast("dni", output_field=CharField()),
                cuil_text=Cast("cuil", output_field=CharField()),
            )
            .order_by("nombres", "dni")
        )

        query = self.request.GET.get("q", "").strip()
        if not query:
            return queryset

        filtros = (
            Q(nombres__icontains=query)
            | Q(email__icontains=query)
            | Q(dni_text__icontains=query)
            | Q(cuil_text__icontains=query)
            | Q(id_estado__dsc_estado__icontains=query)
            | Q(id_ocupacion__dsc_ocupacion__icontains=query)
            | Q(id_ciclo_vida__dsc_ciclo_vida__icontains=query)
        )
        return queryset.filter(filtros)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query"] = self.request.GET.get("q", "").strip()
        context["total_resultados"] = self.object_list.count()
        return context


class PsicologoFormView(View):
    template_name = "psicologo/psicologo_form.html"
    success_url = reverse_lazy("usuario:psicologo_list")
    success_action = "guardado"

    def get_psicologo_queryset(self):
        return Psicologo.objects.select_related("id_estado", "id_rama")

    def get_psicologo(self):
        pk = self.kwargs.get("pk")
        if pk is None:
            return None
        return get_object_or_404(self.get_psicologo_queryset(), pk=pk)

    def get_datos_instance(self, psicologo):
        if not psicologo:
            return None
        return getattr(psicologo, "datos_personales_rel", None)

    def assign_datos_relation(self, datos_personales, psicologo):
        datos_personales.psicologo = psicologo
        datos_personales.paciente = None

    def get_context(self, form, datos_form, psicologo):
        return {
            "form": form,
            "datos_form": datos_form,
            "psicologo": psicologo,
            "modo_edicion": psicologo is not None,
            "cancel_url": self.success_url,
            "form_steps": self.build_form_steps(form, datos_form),
        }

    def build_form_steps(self, form, datos_form):
        steps = [
            {
                "slug": "datos-basicos",
                "title": "Datos basicos",
                "description": "Completa tus datos personales y crea tu acceso a la plataforma de manera simple y segura.",
                "fields": [
                    form["nombres"],
                    form["email"],
                    form["dni"],
                    form["cuil"],
                    form["password1"],
                    form["password2"],
                ],
            },
            {
                "slug": "contacto",
                "title": "Contacto",
                "description": "Carga fecha de nacimiento y datos personales de contacto.",
                "fields": [
                    form["fch_nacimiento"],
                    datos_form["telefono"],
                    datos_form["domicilio"],
                    datos_form["id_sexo"],
                    datos_form["id_std_civil"],
                ],
            },
            {
                "slug": "ubicacion",
                "title": "Ubicacion",
                "description": "Indica el lugar de residencia para completar el perfil profesional.",
                "fields": [
                    datos_form["id_pais"],
                    datos_form["id_provincia"],
                    datos_form["id_localidad"],
                    datos_form["id_zona"],
                ],
            },
            {
                "slug": "perfil",
                "title": "Perfil profesional",
                "description": "Selecciona la rama profesional y agrega una foto si deseas.",
                "fields": [
                    form["id_rama"],
                    form["titulo"],
                    form["foto"],
                ],
            },
        ]

        for index, step in enumerate(steps, start=1):
            step["index"] = index
            step["has_errors"] = any(bound_field.errors for bound_field in step["fields"])

        return steps

    def get(self, request, *args, **kwargs):
        psicologo = self.get_psicologo()
        form = PsicologoForm(instance=psicologo)
        datos_form = DatosPersonalesForm(instance=self.get_datos_instance(psicologo))
        return render(request, self.template_name, self.get_context(form, datos_form, psicologo))

    def post(self, request, *args, **kwargs):
        psicologo = self.get_psicologo()
        form = PsicologoForm(request.POST, request.FILES, instance=psicologo)
        datos_form = DatosPersonalesForm(
            request.POST,
            instance=self.get_datos_instance(psicologo),
        )

        form_is_valid = form.is_valid()
        if form_is_valid:
            self.assign_datos_relation(datos_form.instance, form.save(commit=False))

        if not (form_is_valid and datos_form.is_valid()):
            return render(request, self.template_name, self.get_context(form, datos_form, psicologo))

        with transaction.atomic():
            psicologo = form.save()
            form.save_auth_user(psicologo)
            datos_personales = datos_form.save(commit=False)
            self.assign_datos_relation(datos_personales, psicologo)
            datos_personales.save()

        messages.success(request, f"Psicologo {self.success_action} correctamente.")
        return redirect(self.success_url)


class PsicologoCreateView(PsicologoFormView):
    template_name = "psicologo/psicologo_form.html"
    success_url = reverse_lazy("usuario:psicologo_pendiente_list")
    success_action = "creado"

    def get(self, request, *args, **kwargs):
        form = PsicologoPendienteForm()
        datos_form = DatosPersonalesSolicitudForm()
        return render(request, self.template_name, self.get_context(form, datos_form, None))

    def post(self, request, *args, **kwargs):
        form = PsicologoPendienteForm(request.POST, request.FILES)
        datos_form = DatosPersonalesSolicitudForm(request.POST)

        if not (form.is_valid() and datos_form.is_valid()):
            return render(request, self.template_name, self.get_context(form, datos_form, None))

        with transaction.atomic():
            solicitud = form.save(commit=False)
            for field_name, value in datos_form.cleaned_data.items():
                setattr(solicitud, field_name, value)
            solicitud.save()

        messages.success(
            request,
            "Solicitud enviada correctamente. Quedara pendiente hasta que sea aprobada.",
        )
        return redirect(self.success_url)


class PsicologoUpdateView(PsicologoFormView):
    success_action = "actualizado"


class PsicologoPendienteApproveView(View):
    success_url = reverse_lazy("usuario:psicologo_pendiente_list")

    def post(self, request, pk, *args, **kwargs):
        solicitud = get_object_or_404(PsicologoPendiente, pk=pk)

        if solicitud.estado != PsicologoPendiente.ESTADO_PENDIENTE:
            messages.warning(request, "Esta solicitud ya fue revisada.")
            return redirect(self.success_url)

        estado_activo = PsicologoForm.get_default_estado()
        if estado_activo is None:
            messages.error(request, "No hay un estado ACTIVO configurado para aprobar psicologos.")
            return redirect(self.success_url)

        if self.has_approval_conflicts(solicitud):
            messages.error(
                request,
                "No se puede aprobar porque ya existe un psicologo o usuario con el mismo DNI, CUIL o email.",
            )
            return redirect(self.success_url)

        with transaction.atomic():
            psicologo = Psicologo.objects.create(
                nombres=solicitud.nombres,
                email=solicitud.email,
                dni=solicitud.dni,
                cuil=solicitud.cuil,
                fch_nacimiento=solicitud.fch_nacimiento,
                foto=solicitud.foto,
                id_estado=estado_activo,
                id_rama=solicitud.id_rama,
                titulo=solicitud.titulo,
            )
            DatosPersonales.objects.create(
                psicologo=psicologo,
                telefono=solicitud.telefono,
                domicilio=solicitud.domicilio,
                id_sexo=solicitud.id_sexo,
                id_std_civil=solicitud.id_std_civil,
                id_pais=solicitud.id_pais,
                id_provincia=solicitud.id_provincia,
                id_localidad=solicitud.id_localidad,
                id_zona=solicitud.id_zona,
            )
            self.create_auth_user(solicitud, psicologo)
            solicitud.estado = PsicologoPendiente.ESTADO_APROBADO
            solicitud.psicologo = psicologo
            solicitud.fch_resolucion = timezone.now()
            solicitud.save(update_fields=["estado", "psicologo", "fch_resolucion", "fch_actualizacion"])

        messages.success(request, "Solicitud aprobada. El psicologo ya fue creado.")
        return redirect(self.success_url)

    @staticmethod
    def has_approval_conflicts(solicitud):
        psicologos = Psicologo.objects.filter(
            Q(dni=solicitud.dni) | Q(email__iexact=solicitud.email)
        )
        if solicitud.cuil:
            psicologos = psicologos | Psicologo.objects.filter(cuil=solicitud.cuil)

        username_exists = get_user_model().objects.filter(username=str(solicitud.dni)).exists()
        return psicologos.exists() or username_exists

    @staticmethod
    def create_auth_user(solicitud, psicologo):
        UserModel = get_user_model()
        user = UserModel(username=str(psicologo.dni), email=psicologo.email)
        if hasattr(user, "first_name"):
            user.first_name = psicologo.nombres[:150]
        user.password = solicitud.password_hash
        user.save()
        return user


class PsicologoPendienteRejectView(View):
    success_url = reverse_lazy("usuario:psicologo_pendiente_list")

    def post(self, request, pk, *args, **kwargs):
        solicitud = get_object_or_404(PsicologoPendiente, pk=pk)

        if solicitud.estado != PsicologoPendiente.ESTADO_PENDIENTE:
            messages.warning(request, "Esta solicitud ya fue revisada.")
            return redirect(self.success_url)

        solicitud.estado = PsicologoPendiente.ESTADO_RECHAZADO
        solicitud.fch_resolucion = timezone.now()
        solicitud.save(update_fields=["estado", "fch_resolucion", "fch_actualizacion"])

        messages.success(request, "Solicitud rechazada correctamente.")
        return redirect(self.success_url)


class PacienteFormView(View):
    template_name = "paciente/paciente_form.html"
    success_url = reverse_lazy("usuario:paciente_list")
    success_action = "guardado"

    def get_paciente_queryset(self):
        return Paciente.objects.select_related(
            "id_estado",
            "id_ocupacion",
            "id_ciclo_vida",
            "id_grado_estudio",
        )

    def get_paciente(self):
        pk = self.kwargs.get("pk")
        if pk is None:
            return None
        return get_object_or_404(self.get_paciente_queryset(), pk=pk)

    def get_datos_instance(self, paciente):
        if not paciente:
            return None
        return getattr(paciente, "datos_personales_rel", None)

    def assign_datos_relation(self, datos_personales, paciente):
        datos_personales.paciente = paciente
        datos_personales.psicologo = None

    def get_context(self, form, datos_form, paciente):
        return {
            "form": form,
            "datos_form": datos_form,
            "paciente": paciente,
            "modo_edicion": paciente is not None,
            "cancel_url": self.success_url,
            "form_steps": self.build_form_steps(form, datos_form),
        }

    def build_form_steps(self, form, datos_form):
        steps = [
            {
                "slug": "datos-basicos",
                "title": "Datos basicos",
                "description": "Completa tus datos personales y crea tu acceso a la plataforma de manera simple y segura.",
                "fields": [
                    form["nombres"],
                    form["email"],
                    form["dni"],
                    form["cuil"],
                    form["password1"],
                    form["password2"],
                ],
            },
            {
                "slug": "contacto",
                "title": "Contacto",
                "description": "Carga fecha de nacimiento y datos personales de contacto.",
                "fields": [
                    form["fch_nacimiento"],
                    datos_form["telefono"],
                    datos_form["domicilio"],
                    datos_form["id_sexo"],
                    datos_form["id_std_civil"],
                ],
            },
            {
                "slug": "ubicacion",
                "title": "Ubicacion",
                "description": "Indica el lugar de residencia para completar la ficha del paciente.",
                "fields": [
                    datos_form["id_pais"],
                    datos_form["id_provincia"],
                    datos_form["id_localidad"],
                    datos_form["id_zona"],
                ],
            },
            {
                "slug": "perfil",
                "title": "Ficha del paciente",
                "description": (
                    "Completa ocupacion y grado de estudio. El ciclo de vida se calcula automaticamente "
                    "segun la fecha de nacimiento."
                ),
                "fields": [
                    form["id_ocupacion"],
                    form["id_grado_estudio"],
                    form["foto"],
                ],
            },
        ]

        for index, step in enumerate(steps, start=1):
            step["index"] = index
            step["has_errors"] = any(bound_field.errors for bound_field in step["fields"])

        return steps

    def get(self, request, *args, **kwargs):
        paciente = self.get_paciente()
        form = PacienteForm(instance=paciente)
        datos_form = DatosPersonalesForm(instance=self.get_datos_instance(paciente))
        return render(request, self.template_name, self.get_context(form, datos_form, paciente))

    def post(self, request, *args, **kwargs):
        paciente = self.get_paciente()
        form = PacienteForm(request.POST, request.FILES, instance=paciente)
        datos_form = DatosPersonalesForm(
            request.POST,
            instance=self.get_datos_instance(paciente),
        )

        form_is_valid = form.is_valid()
        if form_is_valid:
            self.assign_datos_relation(datos_form.instance, form.save(commit=False))

        if not (form_is_valid and datos_form.is_valid()):
            return render(request, self.template_name, self.get_context(form, datos_form, paciente))

        with transaction.atomic():
            paciente = form.save()
            form.save_auth_user(paciente)
            datos_personales = datos_form.save(commit=False)
            self.assign_datos_relation(datos_personales, paciente)
            datos_personales.save()

        messages.success(request, f"Paciente {self.success_action} correctamente.")
        return redirect(self.success_url)


class PacienteCreateView(PacienteFormView):
    success_action = "creado"


class PacienteUpdateView(PacienteFormView):
    success_action = "actualizado"


class PsicologoOficinaListView(PsicologoOwnerOrStaffMixin, ListView):
    model = PsicologoOficina
    template_name = "psicologo/oficina_list.html"
    context_object_name = "oficinas"

    def get_queryset(self):
        queryset = PsicologoOficina.objects.select_related(
            "id_psicologo",
            "id_pais",
            "id_provincia",
            "id_localidad",
            "id_zona",
            "id_estado",
        ).order_by("id_psicologo__nombres", "domicilio")
        queryset = self.get_owner_filtered_queryset(queryset)
        query = self.request.GET.get("q", "").strip()
        if query:
            queryset = queryset.filter(
                Q(id_psicologo__nombres__icontains=query)
                | Q(domicilio__icontains=query)
                | Q(telefono__icontains=query)
                | Q(id_pais__dsc_pais__icontains=query)
                | Q(id_provincia__dsc_provincia__icontains=query)
                | Q(id_localidad__dsc_localidad__icontains=query)
                | Q(id_zona__dsc_zona__icontains=query)
                | Q(id_estado__dsc_estado__icontains=query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query"] = self.request.GET.get("q", "").strip()
        context["total_resultados"] = self.object_list.count()
        return context


class PsicologoOficinaCreateView(PsicologoOwnerOrStaffMixin, CreateView):
    model = PsicologoOficina
    form_class = PsicologoOficinaForm
    template_name = "psicologo/oficina_form.html"
    success_url = reverse_lazy("usuario:psicologo_oficina_list")

    def form_valid(self, form):
        messages.success(self.request, "Oficina creada correctamente.")
        return super().form_valid(form)


class PsicologoOficinaUpdateView(PsicologoOwnerOrStaffMixin, UpdateView):
    model = PsicologoOficina
    form_class = PsicologoOficinaForm
    template_name = "psicologo/oficina_form.html"
    success_url = reverse_lazy("usuario:psicologo_oficina_list")

    def get_queryset(self):
        queryset = PsicologoOficina.objects.select_related("id_psicologo")
        return self.get_owner_filtered_queryset(queryset)

    def form_valid(self, form):
        messages.success(self.request, "Oficina actualizada correctamente.")
        return super().form_valid(form)


class PsicologoOficinaDeleteView(PsicologoOwnerOrStaffMixin, DeleteView):
    model = PsicologoOficina
    template_name = "psicologo/oficina_confirm_delete.html"
    context_object_name = "oficina"
    success_url = reverse_lazy("usuario:psicologo_oficina_list")

    def get_queryset(self):
        queryset = PsicologoOficina.objects.select_related("id_psicologo")
        return self.get_owner_filtered_queryset(queryset)

    def form_valid(self, form):
        messages.success(self.request, "Oficina eliminada correctamente.")
        return super().form_valid(form)


class PsicologoMetodoPagoListView(PsicologoOwnerOrStaffMixin, ListView):
    model = PsicologoMetodoPago
    template_name = "psicologo/metodo_pago_list.html"
    context_object_name = "metodos_pago"

    def get_queryset(self):
        queryset = PsicologoMetodoPago.objects.select_related(
            "id_psicologo",
            "id_metodo_pago",
            "id_estado",
        ).order_by("id_psicologo__nombres", "id_metodo_pago__dsc_metodo_pago")
        queryset = self.get_owner_filtered_queryset(queryset)
        query = self.request.GET.get("q", "").strip()
        if query:
            queryset = queryset.filter(
                Q(id_psicologo__nombres__icontains=query)
                | Q(id_metodo_pago__dsc_metodo_pago__icontains=query)
                | Q(id_estado__dsc_estado__icontains=query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query"] = self.request.GET.get("q", "").strip()
        context["total_resultados"] = self.object_list.count()
        return context


class PsicologoMetodoPagoCreateView(PsicologoOwnerOrStaffMixin, CreateView):
    model = PsicologoMetodoPago
    form_class = PsicologoMetodoPagoForm
    template_name = "psicologo/metodo_pago_form.html"
    success_url = reverse_lazy("usuario:psicologo_metodo_pago_list")

    def form_valid(self, form):
        messages.success(self.request, "Metodo de pago creado correctamente.")
        return super().form_valid(form)


class PsicologoMetodoPagoUpdateView(PsicologoOwnerOrStaffMixin, UpdateView):
    model = PsicologoMetodoPago
    form_class = PsicologoMetodoPagoForm
    template_name = "psicologo/metodo_pago_form.html"
    success_url = reverse_lazy("usuario:psicologo_metodo_pago_list")

    def get_queryset(self):
        queryset = PsicologoMetodoPago.objects.select_related("id_psicologo")
        return self.get_owner_filtered_queryset(queryset)

    def form_valid(self, form):
        messages.success(self.request, "Metodo de pago actualizado correctamente.")
        return super().form_valid(form)


class PsicologoMetodoPagoDeleteView(PsicologoOwnerOrStaffMixin, DeleteView):
    model = PsicologoMetodoPago
    template_name = "psicologo/metodo_pago_confirm_delete.html"
    context_object_name = "metodo_pago"
    success_url = reverse_lazy("usuario:psicologo_metodo_pago_list")

    def get_queryset(self):
        queryset = PsicologoMetodoPago.objects.select_related("id_psicologo")
        return self.get_owner_filtered_queryset(queryset)

    def form_valid(self, form):
        messages.success(self.request, "Metodo de pago eliminado correctamente.")
        return super().form_valid(form)


class PsicologoDeleteView(DeleteView):
    model = Psicologo
    template_name = "psicologo/psicologo_confirm_delete.html"
    context_object_name = "psicologo"
    success_url = reverse_lazy("usuario:psicologo_list")

    def form_valid(self, form):
        messages.success(self.request, "Psicologo eliminado correctamente.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cancel_url"] = self.success_url
        return context


class PacienteDeleteView(DeleteView):
    model = Paciente
    template_name = "paciente/paciente_confirm_delete.html"
    context_object_name = "paciente"
    success_url = reverse_lazy("usuario:paciente_list")

    def form_valid(self, form):
        messages.success(self.request, "Paciente eliminado correctamente.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cancel_url"] = self.success_url
        return context
