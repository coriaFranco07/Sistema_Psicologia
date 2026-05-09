import django.db.models.deletion
from django.db import migrations, models


DEFAULT_RAMA_ID = 1
DEFAULT_RAMA_NAME = "SIN ESPECIFICAR"


def crear_rama_por_defecto(apps, schema_editor):
    Rama = apps.get_model("parametro", "Rama")
    Rama.objects.update_or_create(
        id_rama=DEFAULT_RAMA_ID,
        defaults={
            "dsc_rama": DEFAULT_RAMA_NAME,
            "flg_activo": True,
        },
    )


def eliminar_rama_por_defecto(apps, schema_editor):
    Rama = apps.get_model("parametro", "Rama")
    Rama.objects.filter(id_rama=DEFAULT_RAMA_ID, dsc_rama=DEFAULT_RAMA_NAME).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("parametro", "0005_rama"),
        ("usuario", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(crear_rama_por_defecto, eliminar_rama_por_defecto),
        migrations.AddField(
            model_name="psicologo",
            name="id_rama",
            field=models.ForeignKey(
                default=DEFAULT_RAMA_ID,
                on_delete=django.db.models.deletion.RESTRICT,
                related_name="psicologos",
                to="parametro.rama",
                verbose_name="Rama",
            ),
            preserve_default=False,
        ),
    ]
