from django.urls import path
from . import views

app_name = 'permiso'


urlpatterns = [
    path('gestionar-permisos/', views.gestionar_permisos, name='gestionar_permisos'),  
    path('listar-modulo/', views.ModuloListView.as_view(), name='lista_modulo'),
    path('crear-modulo/', views.ModuloCreateView.as_view(), name='crear_modulo'),
    path('editar-modulo/<int:pk>/', views.ModuloEditView.as_view(), name='modulo_edit'),
]