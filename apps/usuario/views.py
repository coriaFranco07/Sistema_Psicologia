from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import transaction
from django.db.models import CharField, Prefetch, Q
from django.db.models.functions import Cast
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, DetailView, ListView, TemplateView, UpdateView
from apps.parametro.models import Provincia, Rama
from apps.core.views import get_estado_activo, get_estado_inactivo
from apps.datos_personales.forms import DatosPersonalesForm
from apps.datos_personales.models import DatosPersonales
from principal.auth_utils import get_panel_role_for_user

from .forms import (
    DatosPersonalesSolicitudForm,
    PacienteForm,
    PacienteSobreMiForm,
    PsicologoForm,
    PsicologoIdiomaForm,
    PsicologoMetodoPagoForm,
    PsicologoOficinaForm,
    PsicologoPendienteForm,
    PsicologoRamaForm,
    PsicologoSobreMiForm,
)

from .models import (
    Paciente,
    Psicologo,
    PsicologoIdioma,
    PsicologoMetodoPago,
    PsicologoOficina,
    PsicologoPendiente,
    PsicologoPendienteRama,
    PsicologoRama,
)


def get_psicologo_ramas_prefetch():
    return Prefetch(
        "ramas",
        queryset=PsicologoRama.objects.select_related("id_rama", "id_estado").filter(
            id_estado__dsc_estado__iexact="ACTIVO",
            id_estado__flg_activo=True,
        ).order_by("id_psico_rama"),
        to_attr="ramas_activas",
    )


def get_psicologo_pendiente_ramas_prefetch():
    return Prefetch(
        "ramas_pendientes",
        queryset=PsicologoPendienteRama.objects.select_related("id_rama").order_by(
            "id_psico_pend_rama"
        ),
        to_attr="ramas_pendientes_prefetch",
    )


class PsicologoMiPerfilView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        psicologo = Psicologo.objects.filter(
            dni=request.user.username
        ).first()

        if psicologo is None:
            messages.error(
                request,
                "No se encontro un perfil de psicologo asociado a este usuario."
            )
            return redirect("panel_psicologo")

        return redirect(
            "usuario:psicologo_detail",
            pk=psicologo.pk
        )


class PacienteMiPerfilView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        paciente = Paciente.objects.filter(
            dni=request.user.username
        ).first()

        if paciente is None:
            messages.error(
                request,
                "No se encontro un perfil de paciente asociado a este usuario."
            )
            return redirect("panel_paciente")

        return redirect(
            "usuario:paciente_detail",
            pk=paciente.pk
        )


class PacienteRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return get_panel_role_for_user(self.request.user) == "paciente"


class PsicologoOwnerOrStaffMixin(LoginRequiredMixin, UserPassesTestMixin):
    psicologo_owner_field = "id_psicologo"

    def get_logged_psicologo(self):
        user = self.request.user

        if user.is_staff or user.is_superuser:
            return None

        if not str(user.username).isdigit():
            return None

        return Psicologo.objects.filter(
            dni=int(user.username)
        ).first()

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


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "usuario/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_psicologos"] = Psicologo.objects.count()
        context["total_psicologos_pendientes"] = PsicologoPendiente.objects.filter(
            estado=PsicologoPendiente.ESTADO_PENDIENTE
        ).count()
        context["total_pacientes"] = Paciente.objects.count()
        context["ultimos_psicologos"] = Psicologo.objects.select_related(
            "id_estado"
        ).prefetch_related(
            get_psicologo_ramas_prefetch()
        ).order_by("-fch_creacion")[:5]
        context["ultimos_pacientes"] = Paciente.objects.select_related(
            "id_estado", "id_ocupacion", "id_ciclo_vida"
        ).order_by("-fch_creacion")[:5]
        return context


class PsicologoPendienteListView(LoginRequiredMixin, ListView):
    model = PsicologoPendiente
    template_name = "psicologo/psicologo_pendiente.html"
    context_object_name = "solicitudes"
    paginate_by = 10

    def get_queryset(self):
        queryset = (
            PsicologoPendiente.objects.select_related(
                "id_sexo",
                "id_std_civil",
                "id_pais",
                "id_provincia",
                "id_localidad",
                "id_zona",
                "psicologo",
            )
            .prefetch_related(get_psicologo_pendiente_ramas_prefetch())
            .order_by("-fch_creacion")
        )

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
            | Q(ramas_pendientes__id_rama__dsc_rama__icontains=query)
        ).distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query"] = self.request.GET.get("q", "").strip()
        context["estado"] = self.request.GET.get("estado", "").strip().upper()
        context["estados"] = PsicologoPendiente.ESTADOS
        context["total_resultados"] = self.object_list.count()
        return context


class PsicologoPendienteDetailView(LoginRequiredMixin, DetailView):
    model = PsicologoPendiente
    template_name = "psicologo/psicologo_pendiente_detail.html"
    context_object_name = "solicitud"

    def get_queryset(self):
        return PsicologoPendiente.objects.select_related(
            "id_sexo",
            "id_std_civil",
            "id_pais",
            "id_provincia",
            "id_localidad",
            "id_zona",
            "psicologo",
        ).prefetch_related(get_psicologo_pendiente_ramas_prefetch())


class PsicologoListView(LoginRequiredMixin, ListView):
    model = Psicologo
    template_name = "psicologo/psicologo_list.html"
    context_object_name = "psicologos"
    paginate_by = 10

    def get_queryset(self):
        queryset = (
            Psicologo.objects.select_related(
                "id_estado",
                "datos_personales",
                "datos_personales__id_sexo",
                "datos_personales__id_std_civil",
                "datos_personales__id_pais",
                "datos_personales__id_provincia",
                "datos_personales__id_localidad",
                "datos_personales__id_zona",
            ).prefetch_related(
                get_psicologo_ramas_prefetch()
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
            | Q(ramas__id_rama__dsc_rama__icontains=query)
            | Q(datos_personales__id_sexo__dsc_tipo__icontains=query)
            | Q(datos_personales__id_std_civil__dsc_std_civil__icontains=query)
            | Q(datos_personales__id_pais__dsc_pais__icontains=query)
            | Q(datos_personales__id_provincia__dsc_provincia__icontains=query)
            | Q(datos_personales__id_localidad__dsc_localidad__icontains=query)
            | Q(datos_personales__id_zona__dsc_zona__icontains=query)
        )
        return queryset.filter(filtros).distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query"] = self.request.GET.get("q", "").strip()
        context["total_resultados"] = self.object_list.count()
        return context


class PsicologoDetailView(LoginRequiredMixin, DetailView):
    model = Psicologo
    template_name = "psicologo/psicologo_detail.html"
    context_object_name = "psicologo"

    def get_template_names(self):
        if get_panel_role_for_user(self.request.user) == "paciente":
            return ["psicologo/psicologo_detail.html"]

        return ["psicologo/psicologo_detail_admin.html"]

    def get_queryset(self):
        return Psicologo.objects.select_related(
            "id_estado",
            "datos_personales",
            "datos_personales__id_sexo",
            "datos_personales__id_std_civil",
            "datos_personales__id_pais",
            "datos_personales__id_provincia",
            "datos_personales__id_localidad",
            "datos_personales__id_zona",
        ).prefetch_related(
            get_psicologo_ramas_prefetch(),
            Prefetch(
                "oficinas",
                queryset=PsicologoOficina.objects.select_related(
                    "id_estado",
                    "id_provincia",
                    "id_localidad",
                ).filter(
                    id_estado__dsc_estado__iexact="ACTIVO",
                    id_estado__flg_activo=True,
                ),
                to_attr="oficinas_activas",
            ),
            Prefetch(
                "idiomas",
                queryset=PsicologoIdioma.objects.select_related("id_idioma", "id_estado").filter(
                    id_estado__dsc_estado__iexact="ACTIVO",
                    id_estado__flg_activo=True,
                ),
                to_attr="idiomas_activos",
            ),
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ramas_activas = self.object.get_ramas_activas()
        oficinas_activas = getattr(self.object, "oficinas_activas", [])
        idiomas_activos = getattr(self.object, "idiomas_activos", [])
        context["ramas_activas"] = ramas_activas
        context["ramas_activas_texto"] = ", ".join(
            rama.id_rama.dsc_rama for rama in ramas_activas
        ) or "Sin ramas asignadas"
        context["idiomas_activos_texto"] = ", ".join(
            idioma.id_idioma.dsc_idioma for idioma in idiomas_activos
        ) or "No especificados"
        context["ubicaciones_presenciales"] = [
            f"{oficina.id_provincia}, {oficina.id_localidad}"
            for oficina in oficinas_activas
            if oficina.id_provincia and oficina.id_localidad
        ]
        context["datos_personales"] = self.object.datos_personales_rel
        return context


class PacienteListView(LoginRequiredMixin, ListView):
    model = Paciente
    template_name = "paciente/paciente_list.html"
    context_object_name = "pacientes"
    paginate_by = 10

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


class PacienteDetailView(LoginRequiredMixin, DetailView):
    model = Paciente
    template_name = "paciente/paciente_detail.html"
    context_object_name = "paciente"

    def get_queryset(self):
        return Paciente.objects.select_related(
            "id_estado",
            "id_ocupacion",
            "id_ciclo_vida",
            "id_grado_estudio",
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


class PacienteMisPsicologosView(PacienteRequiredMixin, TemplateView):
    template_name = "paciente/mis_psicologos.html"


class PacienteEncontrarPsicologoListView(PacienteRequiredMixin, ListView):
    model = Psicologo
    template_name = "paciente/encontrar_psicologo.html"
    context_object_name = "psicologos"
    paginate_by = 10

    def get_queryset(self):
        queryset = (
            Psicologo.objects.select_related(
                "id_estado",
                "datos_personales",
                "datos_personales__id_provincia",
                "datos_personales__id_localidad",
                "datos_personales__id_zona",
            )
            .prefetch_related(
                get_psicologo_ramas_prefetch(),
                Prefetch(
                    "oficinas",
                    queryset=PsicologoOficina.objects.select_related("id_estado").filter(
                        id_estado__dsc_estado__iexact="ACTIVO",
                        id_estado__flg_activo=True,
                    ),
                    to_attr="oficinas_activas",
                ),
                Prefetch(
                    "idiomas",
                    queryset=PsicologoIdioma.objects.select_related("id_idioma", "id_estado").filter(
                        id_estado__dsc_estado__iexact="ACTIVO",
                        id_estado__flg_activo=True,
                    ),
                    to_attr="idiomas_activos",
                ),
            )
            .annotate(
                dni_text=Cast("dni", output_field=CharField()),
            )
            .filter(
                id_estado__dsc_estado__iexact="ACTIVO",
                id_estado__flg_activo=True,
            )
            .order_by("nombres", "dni")
        )

        query = self.request.GET.get("q", "").strip()

        rama = self.request.GET.get("rama", "").strip()
        modalidad = self.request.GET.get("modalidad", "").strip()
        provincia = self.request.GET.get("provincia", "").strip()

        if rama.isdigit():
            queryset = queryset.filter(
                ramas__id_rama_id=int(rama),
                ramas__id_estado__dsc_estado__iexact="ACTIVO",
                ramas__id_estado__flg_activo=True,
            )

        if modalidad == "presencial":
            queryset = queryset.filter(
                oficinas__id_estado__dsc_estado__iexact="ACTIVO",
                oficinas__id_estado__flg_activo=True,
            )

        if provincia.isdigit():
            provincia_id = int(provincia)
            queryset = queryset.filter(
                Q(datos_personales__id_provincia_id=provincia_id)
                | Q(
                    oficinas__id_provincia_id=provincia_id,
                    oficinas__id_estado__dsc_estado__iexact="ACTIVO",
                    oficinas__id_estado__flg_activo=True,
                )
            )

        if not query:
            return queryset.distinct()

        return queryset.filter(
            Q(nombres__icontains=query)
            | Q(email__icontains=query)
            | Q(dni_text__icontains=query)
            | Q(ramas__id_rama__dsc_rama__icontains=query)
            | Q(datos_personales__id_localidad__dsc_localidad__icontains=query)
            | Q(datos_personales__id_provincia__dsc_provincia__icontains=query)
            | Q(datos_personales__id_zona__dsc_zona__icontains=query)
            | Q(oficinas__id_localidad__dsc_localidad__icontains=query)
            | Q(oficinas__id_provincia__dsc_provincia__icontains=query)
        ).distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query"] = self.request.GET.get("q", "").strip()
        context["rama_seleccionada"] = self.request.GET.get("rama", "").strip()
        context["modalidad_seleccionada"] = self.request.GET.get("modalidad", "").strip()
        context["provincia_seleccionada"] = self.request.GET.get("provincia", "").strip()
        context["ramas"] = Rama.objects.filter(flg_activo=True).order_by("dsc_rama")
        context["provincias"] = Provincia.objects.filter(flg_activo=True).order_by("dsc_provincia")
        context["total_resultados"] = self.object_list.count()
        return context


class PsicologoFormView(LoginRequiredMixin, View):
    template_name = "psicologo/psicologo_form.html"
    success_url = reverse_lazy("usuario:psicologo_list")
    success_action = "guardado"

    def get_psicologo_queryset(self):
        return Psicologo.objects.select_related("id_estado").prefetch_related(
            get_psicologo_ramas_prefetch()
        )

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
        if "ramas" in form.fields:
            perfil_description = "Selecciona una o mas ramas profesionales y adjunta tu titulo para enviar la solicitud."
            perfil_fields = [
                form["ramas"],
                form["titulo"],
                form["foto"],
                form["sobre_mi"],
            ]
        else:
            perfil_description = "Selecciona la rama profesional, define el valor por sesion y agrega una foto si deseas."
            perfil_fields = [
                form["titulo"],
                form["foto"],
                form["sobre_mi"],
            ]

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
                "description": perfil_description,
                "fields": perfil_fields,
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


class PsicologoPendienteApproveView(LoginRequiredMixin, View):
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
                titulo=solicitud.titulo,
                sobre_mi=solicitud.sobre_mi,
            )
            PsicologoRama.objects.bulk_create(
                [
                    PsicologoRama(
                        id_psicologo=psicologo,
                        id_rama=rama,
                        valor_sesion=0,
                        id_estado=estado_activo,
                    )
                    for rama in solicitud.get_ramas_pendientes()
                ]
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


class PsicologoPendienteRejectView(LoginRequiredMixin, View):
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


class PacienteFormView(LoginRequiredMixin, View):
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
    paginate_by = 10

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
        context["mostrar_columna_psicologo"] = self.user_is_staff()
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


class EstadoToggleMixin:
    activate_success_message = ""
    deactivate_success_message = ""

    @staticmethod
    def estado_es_inactivo(estado):
        return bool(
            estado and (getattr(estado, "dsc_estado", "") or "").strip().upper() == "INACTIVO"
        )

    def object_is_inactive(self, obj=None):
        current_object = obj or getattr(self, "object", None) or self.get_object()
        return self.estado_es_inactivo(getattr(current_object, "id_estado", None))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_object = getattr(self, "object", None) or self.get_object()
        context["is_inactive"] = self.object_is_inactive(current_object)
        return context

    def form_valid(self, form):
        self.object = self.get_object()

        if self.object_is_inactive(self.object):
            estado_destino = get_estado_activo()
            if estado_destino is None:
                messages.error(self.request, "No hay un estado ACTIVO configurado.")
                return redirect(self.success_url)
            success_message = self.activate_success_message
        else:
            estado_destino = get_estado_inactivo()
            if estado_destino is None:
                messages.error(self.request, "No hay un estado INACTIVO configurado.")
                return redirect(self.success_url)
            success_message = self.deactivate_success_message

        self.object.id_estado = estado_destino
        self.object.save(update_fields=["id_estado"])

        messages.success(self.request, success_message)
        return redirect(self.success_url)


class PsicologoOficinaDeleteView(EstadoToggleMixin, PsicologoOwnerOrStaffMixin, DeleteView):
    model = PsicologoOficina
    template_name = "psicologo/oficina_confirm_delete.html"
    context_object_name = "oficina"
    success_url = reverse_lazy("usuario:psicologo_oficina_list")
    activate_success_message = "Oficina activada correctamente."
    deactivate_success_message = "Oficina dada de baja correctamente."

    def get_queryset(self):
        queryset = PsicologoOficina.objects.select_related("id_psicologo")
        return self.get_owner_filtered_queryset(queryset)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.pop("user", None)
        kwargs.pop("psicologo", None)
        return kwargs

class PsicologoMetodoPagoListView(PsicologoOwnerOrStaffMixin, ListView):
    model = PsicologoMetodoPago
    template_name = "psicologo/metodo_pago_list.html"
    context_object_name = "metodos_pago"
    paginate_by = 10

    def get_queryset(self):
        queryset = PsicologoMetodoPago.objects.select_related(
            "id_psicologo",
            "id_metodo_pago",
            "id_estado",
        ).order_by("id_psicologo__nombres", "id_metodo_pago__dsc_met_pago")
        queryset = self.get_owner_filtered_queryset(queryset)
        query = self.request.GET.get("q", "").strip()
        if query:
            queryset = queryset.filter(
                Q(id_psicologo__nombres__icontains=query)
                | Q(id_metodo_pago__dsc_met_pago__icontains=query)
                | Q(id_estado__dsc_estado__icontains=query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query"] = self.request.GET.get("q", "").strip()
        context["total_resultados"] = self.object_list.count()
        context["mostrar_columna_psicologo"] = self.user_is_staff()
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


class PsicologoMetodoPagoDeleteView(EstadoToggleMixin, PsicologoOwnerOrStaffMixin, DeleteView):
    model = PsicologoMetodoPago
    template_name = "psicologo/metodo_pago_confirm_delete.html"
    context_object_name = "metodo_pago"
    success_url = reverse_lazy("usuario:psicologo_metodo_pago_list")
    activate_success_message = "Metodo de pago activado correctamente."
    deactivate_success_message = "Metodo de pago dado de baja correctamente."

    def get_queryset(self):
        queryset = PsicologoMetodoPago.objects.select_related("id_psicologo")
        return self.get_owner_filtered_queryset(queryset)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.pop("user", None)
        kwargs.pop("psicologo", None)
        return kwargs


class PsicologoRamaListView(PsicologoOwnerOrStaffMixin, ListView):
    model = PsicologoRama
    template_name = "psicologo/rama_list.html"
    context_object_name = "ramas"
    paginate_by = 10

    def get_queryset(self):
        queryset = PsicologoRama.objects.select_related(
            "id_psicologo",
            "id_rama",
            "id_estado",
        ).order_by("id_psicologo__nombres", "id_rama__dsc_rama")
        queryset = self.get_owner_filtered_queryset(queryset)
        query = self.request.GET.get("q", "").strip()
        if query:
            queryset = queryset.filter(
                Q(id_psicologo__nombres__icontains=query)
                | Q(id_rama__dsc_rama__icontains=query)
                | Q(id_estado__dsc_estado__icontains=query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query"] = self.request.GET.get("q", "").strip()
        context["total_resultados"] = self.object_list.count()
        context["mostrar_columna_psicologo"] = self.user_is_staff()
        return context


class PsicologoRamaCreateView(PsicologoOwnerOrStaffMixin, CreateView):
    model = PsicologoRama
    form_class = PsicologoRamaForm
    template_name = "psicologo/rama_form.html"
    success_url = reverse_lazy("usuario:psicologo_rama_list")

    def form_valid(self, form):
        messages.success(self.request, "Rama profesional creada correctamente.")
        return super().form_valid(form)


class PsicologoRamaUpdateView(PsicologoOwnerOrStaffMixin, UpdateView):
    model = PsicologoRama
    form_class = PsicologoRamaForm
    template_name = "psicologo/rama_form.html"
    success_url = reverse_lazy("usuario:psicologo_rama_list")

    def get_queryset(self):
        queryset = PsicologoRama.objects.select_related("id_psicologo")
        return self.get_owner_filtered_queryset(queryset)

    def form_valid(self, form):
        messages.success(self.request, "Rama profesional actualizada correctamente.")
        return super().form_valid(form)


class PsicologoRamaDeleteView(EstadoToggleMixin, PsicologoOwnerOrStaffMixin, DeleteView):
    model = PsicologoRama
    template_name = "psicologo/rama_confirm_delete.html"
    context_object_name = "psicologo_rama"
    success_url = reverse_lazy("usuario:psicologo_rama_list")
    activate_success_message = "Rama profesional activada correctamente."
    deactivate_success_message = "Rama profesional dada de baja correctamente."

    def get_queryset(self):
        queryset = PsicologoRama.objects.select_related("id_psicologo", "id_rama")
        return self.get_owner_filtered_queryset(queryset)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.pop("user", None)
        kwargs.pop("psicologo", None)
        return kwargs


class PsicologoDeleteView(EstadoToggleMixin, LoginRequiredMixin, DeleteView):
    model = Psicologo
    template_name = "psicologo/psicologo_confirm_delete.html"
    context_object_name = "psicologo"
    success_url = reverse_lazy("usuario:psicologo_list")
    activate_success_message = "Psicologo activado correctamente."
    deactivate_success_message = "Psicologo dado de baja correctamente."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cancel_url"] = self.success_url
        return context


class PacienteDeleteView(EstadoToggleMixin, LoginRequiredMixin, DeleteView):
    model = Paciente
    template_name = "paciente/paciente_confirm_delete.html"
    context_object_name = "paciente"
    success_url = reverse_lazy("usuario:paciente_list")
    activate_success_message = "Paciente activado correctamente."
    deactivate_success_message = "Paciente dado de baja correctamente."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cancel_url"] = self.success_url
        return context



class PsicologoIdiomaListView(PsicologoOwnerOrStaffMixin, ListView):
    model = PsicologoIdioma
    template_name = "psicologo/idioma_list.html"
    context_object_name = "idiomas"
    paginate_by = 10

    def get_queryset(self):
        queryset = PsicologoIdioma.objects.select_related(
            "id_psicologo",
            "id_idioma",
            "id_estado",
        ).order_by("id_psicologo__nombres", "id_idioma__dsc_idioma")

        queryset = self.get_owner_filtered_queryset(queryset)

        query = self.request.GET.get("q", "").strip()
        if query:
            queryset = queryset.filter(
                Q(id_psicologo__nombres__icontains=query)
                | Q(id_idioma__dsc_idioma__icontains=query)
                | Q(id_estado__dsc_estado__icontains=query)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query"] = self.request.GET.get("q", "").strip()
        context["total_resultados"] = self.object_list.count()
        context["mostrar_columna_psicologo"] = self.user_is_staff()
        return context


class PsicologoIdiomaCreateView(PsicologoOwnerOrStaffMixin, CreateView):
    model = PsicologoIdioma
    form_class = PsicologoIdiomaForm
    template_name = "psicologo/idioma_form.html"
    success_url = reverse_lazy("usuario:psicologo_idioma_list")

    def form_valid(self, form):
        messages.success(self.request, "Idioma creado correctamente.")
        return super().form_valid(form)


class PsicologoIdiomaUpdateView(PsicologoOwnerOrStaffMixin, UpdateView):
    model = PsicologoIdioma
    form_class = PsicologoIdiomaForm
    template_name = "psicologo/idioma_form.html"
    success_url = reverse_lazy("usuario:psicologo_idioma_list")

    def get_queryset(self):
        queryset = PsicologoIdioma.objects.select_related("id_psicologo")
        return self.get_owner_filtered_queryset(queryset)

    def form_valid(self, form):
        messages.success(self.request, "Idioma actualizado correctamente.")
        return super().form_valid(form)


class PsicologoIdiomaDeleteView(EstadoToggleMixin, PsicologoOwnerOrStaffMixin, DeleteView):
    model = PsicologoIdioma
    template_name = "psicologo/idioma_confirm_delete.html"
    context_object_name = "idioma"
    success_url = reverse_lazy("usuario:psicologo_idioma_list")
    activate_success_message = "Idioma activado correctamente."
    deactivate_success_message = "Idioma dado de baja correctamente."

    def get_queryset(self):
        queryset = PsicologoIdioma.objects.select_related("id_psicologo")
        return self.get_owner_filtered_queryset(queryset)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.pop("user", None)
        kwargs.pop("psicologo", None)
        return kwargs
    

class PsicologoSobreMiUpdateView(LoginRequiredMixin, UpdateView):
    model = Psicologo
    form_class = PsicologoSobreMiForm
    template_name = "psicologo/psicologo_sobre_mi_form.html"
    context_object_name = "psicologo"

    def get_success_url(self):
        return reverse_lazy("usuario:psicologo_detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, "Sobre mí actualizado correctamente.")
        return super().form_valid(form)
    

class PacienteSobreMiUpdateView(LoginRequiredMixin, UpdateView):
    model = Paciente
    form_class = PacienteSobreMiForm
    template_name = "paciente/paciente_sobre_mi_form.html"
    context_object_name = "paciente"

    def get_success_url(self):
        return reverse_lazy("usuario:paciente_detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, "Sobre mí actualizado correctamente.")
        return super().form_valid(form)

