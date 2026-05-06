from django.contrib import messages
from django.db import transaction
from django.db.models import CharField, Q
from django.db.models.functions import Cast
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import DeleteView, ListView, TemplateView

from apps.datos_personales.forms import DatosPersonalesForm
from apps.datos_personales.models import DatosPersonales

from .forms import PacienteForm, PsicologoForm
from .models import Paciente, Psicologo


class DashboardView(TemplateView):
    template_name = "usuario/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_psicologos"] = Psicologo.objects.count()
        context["total_pacientes"] = Paciente.objects.count()
        context["ultimos_psicologos"] = Psicologo.objects.select_related("id_estado").order_by(
            "-fch_creacion"
        )[:5]
        context["ultimos_pacientes"] = Paciente.objects.select_related(
            "id_estado", "id_ocupacion", "id_ciclo_vida"
        ).order_by("-fch_creacion")[:5]
        return context


class BasePersonaListView(ListView):
    template_name = "usuario/persona_list.html"
    context_object_name = "personas"
    create_url_name = ""
    update_url_name = ""
    delete_url_name = ""
    entity_label = ""
    entity_label_plural = ""
    extra_search_fields = ()
    select_related_fields = ()

    def get_queryset(self):
        queryset = (
            self.model.objects.select_related("id_estado", "datos_personales", *self.select_related_fields)
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
        )

        for field_name in self.extra_search_fields:
            filtros |= Q(**{f"{field_name}__icontains": query})

        return queryset.filter(filtros)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["entity_label"] = self.entity_label
        context["entity_label_plural"] = self.entity_label_plural
        context["create_url_name"] = self.create_url_name
        context["update_url_name"] = self.update_url_name
        context["delete_url_name"] = self.delete_url_name
        context["query"] = self.request.GET.get("q", "").strip()
        context["total_resultados"] = self.get_queryset().count()
        return context


class PsicologoListView(BasePersonaListView):
    model = Psicologo
    entity_label = "Psicologo"
    entity_label_plural = "Psicologos"
    create_url_name = "usuario:psicologo_create"
    update_url_name = "usuario:psicologo_update"
    delete_url_name = "usuario:psicologo_delete"


class PacienteListView(BasePersonaListView):
    model = Paciente
    entity_label = "Paciente"
    entity_label_plural = "Pacientes"
    create_url_name = "usuario:paciente_create"
    update_url_name = "usuario:paciente_update"
    delete_url_name = "usuario:paciente_delete"
    extra_search_fields = ("id_ocupacion__dsc_ocupacion", "id_ciclo_vida__dsc_ciclo_vida")
    select_related_fields = ("id_ocupacion", "id_ciclo_vida", "id_grado_estudio")


class BasePersonaFormView(View):
    model = None
    form_class = None
    relation_field = ""
    template_name = "usuario/persona_form.html"
    success_url = None
    entity_label = ""
    success_action = "guardado"
    select_related_fields = ()

    def get_persona_queryset(self):
        return self.model.objects.select_related(
            "id_estado",
            *self.select_related_fields,
        )

    def get_object(self):
        pk = self.kwargs.get("pk")
        if pk is None:
            return None
        return get_object_or_404(self.get_persona_queryset(), pk=pk)

    def get_datos_instance(self, persona):
        if not persona:
            return None
        return getattr(persona, "datos_personales_rel", None)

    def get_context(self, form, datos_form, persona):
        return {
            "form": form,
            "datos_form": datos_form,
            "persona": persona,
            "entity_label": self.entity_label,
            "modo_edicion": persona is not None,
            "cancel_url": self.success_url,
        }

    def get(self, request, *args, **kwargs):
        persona = self.get_object()
        form = self.form_class(instance=persona)
        datos_form = DatosPersonalesForm(instance=self.get_datos_instance(persona))
        return render(request, self.template_name, self.get_context(form, datos_form, persona))

    def post(self, request, *args, **kwargs):
        persona = self.get_object()
        form = self.form_class(request.POST, request.FILES, instance=persona)
        datos_form = DatosPersonalesForm(
            request.POST,
            instance=self.get_datos_instance(persona),
        )

        if not (form.is_valid() and datos_form.is_valid()):
            return render(request, self.template_name, self.get_context(form, datos_form, persona))

        with transaction.atomic():
            persona = form.save()
            datos_personales = datos_form.save(commit=False)

            if self.relation_field == "psicologo":
                datos_personales.psicologo = persona
                datos_personales.paciente = None
            else:
                datos_personales.paciente = persona
                datos_personales.psicologo = None

            datos_personales.save()

        messages.success(request, f"{self.entity_label} {self.success_action} correctamente.")
        return redirect(self.success_url)


class BasePersonaCreateView(BasePersonaFormView):
    success_action = "creado"


class BasePersonaUpdateView(BasePersonaFormView):
    success_action = "actualizado"


class PsicologoCreateView(BasePersonaCreateView):
    model = Psicologo
    form_class = PsicologoForm
    relation_field = "psicologo"
    success_url = reverse_lazy("usuario:psicologo_list")
    entity_label = "Psicologo"


class PsicologoUpdateView(BasePersonaUpdateView):
    model = Psicologo
    form_class = PsicologoForm
    relation_field = "psicologo"
    success_url = reverse_lazy("usuario:psicologo_list")
    entity_label = "Psicologo"


class PacienteCreateView(BasePersonaCreateView):
    model = Paciente
    form_class = PacienteForm
    relation_field = "paciente"
    success_url = reverse_lazy("usuario:paciente_list")
    entity_label = "Paciente"
    select_related_fields = ("id_ocupacion", "id_ciclo_vida", "id_grado_estudio")


class PacienteUpdateView(BasePersonaUpdateView):
    model = Paciente
    form_class = PacienteForm
    relation_field = "paciente"
    success_url = reverse_lazy("usuario:paciente_list")
    entity_label = "Paciente"
    select_related_fields = ("id_ocupacion", "id_ciclo_vida", "id_grado_estudio")


class BasePersonaDeleteView(DeleteView):
    template_name = "usuario/persona_confirm_delete.html"
    context_object_name = "persona"
    success_url = None
    entity_label = ""

    def delete(self, request, *args, **kwargs):
        messages.success(request, f"{self.entity_label} eliminado correctamente.")
        return super().delete(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["entity_label"] = self.entity_label
        context["cancel_url"] = self.success_url
        return context


class PsicologoDeleteView(BasePersonaDeleteView):
    model = Psicologo
    success_url = reverse_lazy("usuario:psicologo_list")
    entity_label = "Psicologo"


class PacienteDeleteView(BasePersonaDeleteView):
    model = Paciente
    success_url = reverse_lazy("usuario:paciente_list")
    entity_label = "Paciente"
