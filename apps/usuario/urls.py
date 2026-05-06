
from apps.usuario.utils import deuda_usuario, gestion_usuarios, resetear_password_usuario, socios_por_estado, usuarios_por_estado, usuarios_por_tipo, usuarios_total
from . import views
from django.urls import path
from .views import AdminDocumentoEliminarView, AdminDocumentoSubirView, AdminDocumentosUsuarioPendienteView, AdminDocumentosUsuarioView, AdminDocumentosUsuarioView2, CompletarRelacionPendienteView, ConfirmarPendienteView, FamiliaUsuarioView, ObservacionPendienteView, PendienteDetalleView, PendientesListView, RechazarPendienteView, SocioFliaPendienteCreateView, SocioPendienteCreateView, TipoDocumentoCreate, TipoDocumentoUpdate, TiposDocumentosList, UsuarioAutocomplete, UsuarioAutocomplete3, UsuarioAutocomplete4, UsuarioListView, UsuarioCreateView, UsuarioRelacionAutocomplete, UsuarioRelacionAutocomplete2, UsuarioUpdateView, actualizar_foto_perfil, all_datos_usuario, colocar_fecha_socio_alta, pendientes_datatable, usuarios_datatable

app_name = 'usuario'

urlpatterns = [
    path(
        "datatable/",
        usuarios_datatable,
        name="usuarios_datatable"
    ),
    path(
        "pendientes_datatable/",
        pendientes_datatable,
        name="pendientes_datatable"
    ),
    path("", UsuarioListView.as_view(), name="usuarios_list"),
    path("nuevo_usuario/", UsuarioCreateView.as_view(), name="usuario_create"),
    path("editar_usuario/<int:pk>/", UsuarioUpdateView.as_view(), name="usuario_update"),
    path('completar_relacion/', views.completar_relacion_view, name='completar_relacion'),
    path('gestion/', gestion_usuarios, name='gestion_usuarios'),

    path('socios_por_estado/', socios_por_estado, name='socios_por_estado'),

    path('usuarios/total/', usuarios_total, name='usuarios-total'),
    path('usuarios/estado/<int:id>/', usuarios_por_estado, name='usuarios-por-estado'),
    path('usuarios/tipo/<int:id>/', usuarios_por_tipo, name='usuarios-por-tipo'),

    path("solicitud-alta/<int:id_tipo_socio>/", SocioPendienteCreateView.as_view(), name="solicitud_alta"),

    path('exito_registro_socio_pendiente/', views.exito_registro_socio_pendiente, name='exito_registro_socio_pendiente'),

    path("solicitud-alta-flia/", SocioFliaPendienteCreateView.as_view(), name="solicitud_alta_flia"),

    path("pendientes/", PendientesListView.as_view(), name="pendientes_list"),
    path("pendiente/<uuid:uuid>/", PendienteDetalleView.as_view(), name="pendiente_detalle"),
    path("pendiente/<uuid:uuid>/confirmar/", ConfirmarPendienteView.as_view(), name="confirmar_pendiente"),
    path("pendiente/<uuid:uuid>/rechazar/", RechazarPendienteView.as_view(), name="rechazar_pendiente"),
    
    path("completar-relacion-pendiente/", CompletarRelacionPendienteView.as_view(), name="completar_relacion_pendiente_session"),

    path("pendiente/<uuid:uuid>/observaciones/", ObservacionPendienteView.as_view(), name="observaciones_pendiente"),

    path('api/deuda_usuario/<int:id>/', deuda_usuario, name='deuda_usuario'),

    path('all_datos_usuario/', all_datos_usuario, name='all_datos_usuario'),

    path("colocar_fecha_socio_alta/<uuid:uuid_obj>/", colocar_fecha_socio_alta, name="colocar_fecha_socio_alta"),

    path('usuario-autocomplete/', UsuarioAutocomplete.as_view(), name='usuario-autocomplete'),  
    path(
        'usuario-relacion-autocomplete/',
        UsuarioRelacionAutocomplete.as_view(),
        name='usuario-relacion-autocomplete'
    ), 

    path(
        'usuario-relacion-autocomplete2/',
        UsuarioRelacionAutocomplete2.as_view(),
        name='usuario-relacion-autocomplete2'
    ),

    path('usuario-autocomplete3/', UsuarioAutocomplete3.as_view(), name='usuario-autocomplete3'),

    path('usuario-autocomplete4/', UsuarioAutocomplete4.as_view(), name='usuario-autocomplete4'),  

    path('actualizar_foto_perfil/', actualizar_foto_perfil, name='actualizar_foto_perfil'),

    path(
        "reset-password-usuario/",
        resetear_password_usuario,
        name="reset_password_usuario"
    ),

    path(
        "documentos/",
        TiposDocumentosList.as_view(),
        name="tipo_documento_list"
    ),

    path(
        "documentos_crear/",
        TipoDocumentoCreate.as_view(),
        name="tipo_documento_create"
    ),

    path(
        "documentos_editar/<int:pk>/",
        TipoDocumentoUpdate.as_view(),
        name="tipo_documento_update"
    ),

    path(
        "subir_documento/",
        views.subir_documento,
        name="subir_documento"
    ),

    path(
        "admin_documentos/<str:usuario_id>/",
        AdminDocumentosUsuarioView.as_view(),
        name="admin_documentos_usuario"
    ),

    path(
        "admin_documentos2/<str:usuario_id>/",
        AdminDocumentosUsuarioView2.as_view(),
        name="admin_documentos_usuario2"
    ),

    path(
        "admin_documentos_subir/<str:usuario_id>/",
        AdminDocumentoSubirView.as_view(),
        name="admin_documento_subir"
    ),

    path(
        "admin_documentos_eliminar/<int:doc_id>/",
        AdminDocumentoEliminarView.as_view(),
        name="admin_documento_eliminar"
    ),


    path(
        "admin_documentos_pendiente/<str:uuid>/",
        views.AdminDocumentosUsuarioPendienteView.as_view(),
        name="admin_documentos_usuario_pendiente"
    ),

    path(
        "admin_documentos_pendiente2/<str:uuid>/",
        views.AdminDocumentosUsuarioPendienteView2.as_view(),
        name="admin_documentos_usuario_pendiente2"
    ),

    path(
        "admin_documentos_pendiente/subir/<str:uuid>/",
        views.AdminDocumentoPendienteSubirView.as_view(),
        name="admin_documento_pendiente_subir"
    ),
    path(
        "admin_documentos_pendiente/eliminar/<int:doc_id>/",
        views.AdminDocumentoPendienteEliminarView.as_view(),
        name="admin_documento_pendiente_eliminar"
    ),


    path(
        "familia_usuario",
        FamiliaUsuarioView.as_view(),
        name="familia_usuario"
    ),

    
    path(
        'documentos-tipo-socio/',
        views.DocumentoTipoSocioListView.as_view(),
        name='documento_tipo_socio_list'
    ),
    path(
        'documentos-tipo-socio/crear/',
        views.DocumentoTipoSocioCreateView.as_view(),
        name='documento_tipo_socio_create'
    ),
    path(
        'documentos-tipo-socio/<int:pk>/editar/',
        views.DocumentoTipoSocioUpdateView.as_view(),
        name='documento_tipo_socio_update'
    ),

    path(
        'documentos-relacion/',
        views.DocumentoRelacionListView.as_view(),
        name='documento_relacion_list'
    ),
    path(
        'documentos-relacion/crear/',
        views.DocumentoRelacionCreateView.as_view(),
        name='documento_relacion_create'
    ),
    path(
        'documentos-relacion/<int:pk>/editar/',
        views.DocumentoRelacionUpdateView.as_view(),
        name='documento_relacion_update'
    ),
    
]
