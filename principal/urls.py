from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.views.generic import RedirectView
from django.urls import include, path

from .views import StyledLoginView


urlpatterns = [
    path("", RedirectView.as_view(pattern_name="login", permanent=False), name="root_login"),
    path("login/", StyledLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("admin/", admin.site.urls),
    path("", include(("apps.usuario.urls", "usuario"), namespace="usuario")),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
