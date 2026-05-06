from . import views
from django.urls import path
from .views import DatosPersonalesListView

urlpatterns = [
    path("datos_personales_usuario/<int:pk>/", DatosPersonalesListView.as_view(), name="datos_personales_usuario"),
]
