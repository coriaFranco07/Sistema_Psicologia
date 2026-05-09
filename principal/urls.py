from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.views.generic import TemplateView
from django.urls import include, path

from .views import PanelAdminView, PanelPsicologoView, StyledLoginView


urlpatterns = [
    path("", TemplateView.as_view(template_name="inicio.html"), name="home"),
    path("login/", StyledLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("panel-admin/", PanelAdminView.as_view(), name="panel_admin"),
    path("panel-psicologo/", PanelPsicologoView.as_view(), name="panel_psicologo"),
    path("admin/", admin.site.urls),
    path("", include(("apps.usuario.urls", "usuario"), namespace="usuario")),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
