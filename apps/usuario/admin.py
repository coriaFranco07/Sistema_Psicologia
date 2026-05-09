from django.contrib import admin

from apps.datos_personales.models import DatosPersonales

from .models import Paciente, Psicologo


class PsicologoDatosPersonalesInline(admin.StackedInline):
    model = DatosPersonales
    fk_name = "psicologo"
    extra = 0
    max_num = 1


class PacienteDatosPersonalesInline(admin.StackedInline):
    model = DatosPersonales
    fk_name = "paciente"
    extra = 0
    max_num = 1


@admin.register(Psicologo)
class PsicologoAdmin(admin.ModelAdmin):
    list_display = ("nombres", "dni", "email", "id_estado", "id_rama", "tiene_foto")
    search_fields = ("nombres", "dni", "email", "cuil", "id_rama__dsc_rama")
    list_filter = ("id_estado", "id_rama")
    list_select_related = ("id_estado", "id_rama")
    autocomplete_fields = ("id_estado", "id_rama")
    inlines = [PsicologoDatosPersonalesInline]

    @admin.display(boolean=True, description="Foto")
    def tiene_foto(self, obj):
        return bool(obj.foto)


@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = (
        "nombres",
        "dni",
        "email",
        "id_estado",
        "id_ocupacion",
        "id_ciclo_vida",
    )
    search_fields = ("nombres", "dni", "email", "cuil")
    list_filter = ("id_estado", "id_ocupacion", "id_ciclo_vida", "id_grado_estudio")
    list_select_related = ("id_estado", "id_ocupacion", "id_ciclo_vida", "id_grado_estudio")
    autocomplete_fields = ("id_estado", "id_ocupacion", "id_grado_estudio")
    readonly_fields = ("id_ciclo_vida",)
    inlines = [PacienteDatosPersonalesInline]
