from django.contrib import admin

from apps.datos_personales.models import DatosPersonales

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


class PsicologoPendienteRamaInline(admin.TabularInline):
    model = PsicologoPendienteRama
    fk_name = "id_psicologo_pendiente"
    extra = 0


@admin.register(Psicologo)
class PsicologoAdmin(admin.ModelAdmin):
    list_display = (
        "nombres",
        "dni",
        "email",
        "id_estado",
        "rama_principal",
        "tiene_titulo",
        "tiene_foto",
    )
    search_fields = ("nombres", "dni", "email", "cuil", "ramas__id_rama__dsc_rama")
    list_filter = ("id_estado",)
    list_select_related = ("id_estado",)
    autocomplete_fields = ("id_estado",)
    inlines = [PsicologoDatosPersonalesInline]

    @admin.display(description="Rama")
    def rama_principal(self, obj):
        rama = obj.id_rama
        return rama.dsc_rama if rama else "-"

    @admin.display(boolean=True, description="Foto")
    def tiene_foto(self, obj):
        return bool(obj.foto)

    @admin.display(boolean=True, description="Titulo")
    def tiene_titulo(self, obj):
        return bool(obj.titulo)


@admin.register(PsicologoPendiente)
class PsicologoPendienteAdmin(admin.ModelAdmin):
    list_display = ("nombres", "dni", "email", "ramas", "estado", "fch_creacion")
    search_fields = ("nombres", "dni", "email", "cuil", "ramas_pendientes__id_rama__dsc_rama")
    list_filter = ("estado",)
    list_select_related = ("psicologo",)
    readonly_fields = ("password_hash", "psicologo", "fch_creacion", "fch_actualizacion", "fch_resolucion")
    inlines = [PsicologoPendienteRamaInline]

    @admin.display(description="Ramas")
    def ramas(self, obj):
        return obj.ramas_descripcion


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


@admin.register(PsicologoMetodoPago)
class PsicologoMetodoPagoAdmin(admin.ModelAdmin):
    list_display = ("id_psicologo", "id_metodo_pago", "id_estado")
    search_fields = ("id_psicologo__nombres", "id_metodo_pago__dsc_met_pago")
    list_filter = ("id_estado", "id_metodo_pago")
    list_select_related = ("id_psicologo", "id_metodo_pago", "id_estado")


@admin.register(PsicologoOficina)
class PsicologoOficinaAdmin(admin.ModelAdmin):
    list_display = ("id_psicologo", "domicilio", "telefono", "id_localidad", "id_estado")
    search_fields = ("id_psicologo__nombres", "domicilio", "telefono")
    list_filter = ("id_estado", "id_pais", "id_provincia")
    list_select_related = ("id_psicologo", "id_estado", "id_pais", "id_provincia", "id_localidad")


@admin.register(PsicologoIdioma)
class PsicologoIdiomaAdmin(admin.ModelAdmin):
    list_display = ("id_psicologo", "id_idioma", "id_estado")
    search_fields = ("id_psicologo__nombres", "id_idioma__dsc_idioma")
    list_filter = ("id_estado", "id_idioma")
    list_select_related = ("id_psicologo", "id_idioma", "id_estado")


@admin.register(PsicologoRama)
class PsicologoRamaAdmin(admin.ModelAdmin):
    list_display = ("id_psicologo", "id_rama", "valor_sesion", "id_estado")
    search_fields = ("id_psicologo__nombres", "id_rama__dsc_rama")
    list_filter = ("id_estado", "id_rama")
    list_select_related = ("id_psicologo", "id_rama", "id_estado")


@admin.register(PsicologoPendienteRama)
class PsicologoPendienteRamaAdmin(admin.ModelAdmin):
    list_display = ("id_psicologo_pendiente", "id_rama")
    search_fields = ("id_psicologo_pendiente__nombres", "id_rama__dsc_rama")
    list_select_related = ("id_psicologo_pendiente", "id_rama")
