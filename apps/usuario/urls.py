from django.urls import path

from . import views


app_name = "usuario"


urlpatterns = [
    path("psicologos/", views.PsicologoListView.as_view(), name="psicologo_list"),
    path("psicologos/nuevo/", views.PsicologoCreateView.as_view(), name="psicologo_create"),
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
