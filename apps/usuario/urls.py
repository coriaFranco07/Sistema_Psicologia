from django.urls import path

from . import views


app_name = "usuario"


urlpatterns = [
    path("psicologos/", views.PsicologoListView.as_view(), name="psicologo_list"),
    path("psicologos/nuevo/", views.PsicologoCreateView.as_view(), name="psicologo_create"),
    path("psicologos/<int:pk>/", views.PsicologoDetailView.as_view(), name="psicologo_detail"),
    path(
        "psicologos/pendientes/",
        views.PsicologoPendienteListView.as_view(),
        name="psicologo_pendiente_list",
    ),
    path(
        "psicologos/pendientes/<int:pk>/",
        views.PsicologoPendienteDetailView.as_view(),
        name="psicologo_pendiente_detail",
    ),
    path(
        "psicologos/pendientes/<int:pk>/confirmar/",
        views.PsicologoPendienteApproveView.as_view(),
        name="psicologo_pendiente_confirmar",
    ),
    path(
        "psicologos/pendientes/<int:pk>/rechazar/",
        views.PsicologoPendienteRejectView.as_view(),
        name="psicologo_pendiente_rechazar",
    ),
    path(
        "psicologos/<int:pk>/editar/",
        views.PsicologoUpdateView.as_view(),
        name="psicologo_update",
    ),
    path(
        "psicologos/<int:pk>/eliminar/",
        views.PsicologoDeleteView.as_view(),
        name="psicologo_delete",
    ),
    path(
        "psicologos/oficinas/",
        views.PsicologoOficinaListView.as_view(),
        name="psicologo_oficina_list",
    ),
    path(
        "psicologos/oficinas/nueva/",
        views.PsicologoOficinaCreateView.as_view(),
        name="psicologo_oficina_create",
    ),
    path(
        "psicologos/oficinas/<int:pk>/editar/",
        views.PsicologoOficinaUpdateView.as_view(),
        name="psicologo_oficina_update",
    ),
    path(
        "psicologos/oficinas/<int:pk>/eliminar/",
        views.PsicologoOficinaDeleteView.as_view(),
        name="psicologo_oficina_delete",
    ),
    path(
        "psicologos/metodos-pago/",
        views.PsicologoMetodoPagoListView.as_view(),
        name="psicologo_metodo_pago_list",
    ),
    path(
        "psicologos/metodos-pago/nuevo/",
        views.PsicologoMetodoPagoCreateView.as_view(),
        name="psicologo_metodo_pago_create",
    ),
    path(
        "psicologos/metodos-pago/<int:pk>/editar/",
        views.PsicologoMetodoPagoUpdateView.as_view(),
        name="psicologo_metodo_pago_update",
    ),
    path(
        "psicologos/metodos-pago/<int:pk>/eliminar/",
        views.PsicologoMetodoPagoDeleteView.as_view(),
        name="psicologo_metodo_pago_delete",
    ),
    path(
        "psicologos/idiomas/",
        views.PsicologoIdiomaListView.as_view(),
        name="psicologo_idioma_list",
    ),
    path(
        "psicologos/idiomas/nuevo/",
        views.PsicologoIdiomaCreateView.as_view(),
        name="psicologo_idioma_create",
    ),
    path(
        "psicologos/idiomas/<int:pk>/editar/",
        views.PsicologoIdiomaUpdateView.as_view(),
        name="psicologo_idioma_update",
    ),
    path(
        "psicologos/idiomas/<int:pk>/eliminar/",
        views.PsicologoIdiomaDeleteView.as_view(),
        name="psicologo_idioma_delete",
    ),
    path("pacientes/", views.PacienteListView.as_view(), name="paciente_list"),
    path("pacientes/nuevo/", views.PacienteCreateView.as_view(), name="paciente_create"),
    path(
        "pacientes/<int:pk>/editar/",
        views.PacienteUpdateView.as_view(),
        name="paciente_update",
    ),
    path(
        "pacientes/<int:pk>/eliminar/",
        views.PacienteDeleteView.as_view(),
        name="paciente_delete",
    ),
]
