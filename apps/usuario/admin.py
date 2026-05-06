from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import DocumentoRelacion, Usuario, UsuarioPendiente, DocumentoUsuario, TipoDocumento, DocumentoTipoSocio
from .forms import UsuarioAdminCreationForm, UsuarioAdminChangeForm
from django.utils.html import format_html


class UsuarioAdmin(UserAdmin):
    form = UsuarioAdminChangeForm   # Para editar usuario en admin
    add_form = UsuarioAdminCreationForm  # Para crear usuario desde admin

    model = Usuario
    list_display = (
        'foto_preview',
        'username','email','nombres','dni'
    )
    list_filter = ('is_staff','is_active')
    fieldsets = (
        (None, {
            'fields': (
                'username','email','nombres','dni', 'cuil', 'foto',
                'password','saldo','saldo_gral_flia',
                'es_admin_local','id_std_socio','id_tipo_socio','id_jerarquia', 'operador_sistema'
            )
        }),
        ('Permisos', {
            'fields': (
                'is_staff','is_active','is_superuser',
                'groups','user_permissions'
            )
        }),
        ('Fechas', {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username','email','nombres','dni', 'cuil', 'fch_nacimiento','password1','password2','is_staff','is_active')}
        ),
    )
    search_fields = ('nombres', 'email', 'dni')
    ordering = ('nombres',)

    def foto_preview(self, obj):
        if obj.foto:
            return format_html(
                '<img src="{}" style="width:50px;height:50px;border-radius:50%;" />',
                obj.foto_url
            )
        return "Sin foto"

    foto_preview.short_description = "Foto"


admin.site.register(Usuario, UsuarioAdmin)
admin.site.register(UsuarioPendiente)
admin.site.register(DocumentoUsuario)
admin.site.register(TipoDocumento)
admin.site.register(DocumentoTipoSocio)
admin.site.register(DocumentoRelacion)