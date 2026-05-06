from . import views
from django.urls import path

app_name = 'core'

urlpatterns = [
    path("dashboard_visitas", views.dashboard_visitas, name="dashboard_visitas"),
]
