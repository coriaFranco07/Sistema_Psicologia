from django.contrib import admin, messages
from django.shortcuts import redirect
from django.urls import path
from apps.core.models import LogSistema

@admin.register(LogSistema)
class LogSistemaAdmin(admin.ModelAdmin):
    list_display = ("fecha_hora", "nivel", "usuario", "ruta")
    list_filter = ("nivel", "fecha_hora")
    search_fields = ("mensaje", "detalle", "ruta")
    readonly_fields = [f.name for f in LogSistema._meta.fields]

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "eliminar-todos/",
                self.admin_site.admin_view(self.eliminar_todos),
                name="logs_eliminar_todos",
            ),
        ]
        return custom_urls + urls

    def eliminar_todos(self, request):
        count = LogSistema.objects.count()

        if count > 0:
            batch_size = 1000

            while True:
                ids = list(
                    LogSistema.objects.values_list("id", flat=True)[:batch_size]
                )
                if not ids:
                    break

                LogSistema.objects.filter(id__in=ids).delete()

            self.message_user(
                request,
                f"Se eliminaron {count} registros de log.",
                messages.SUCCESS
            )
        else:
            self.message_user(
                request,
                "No hay registros de log para eliminar.",
                messages.WARNING
            )

        return redirect(request.META.get("HTTP_REFERER", ".."))