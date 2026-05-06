from django.db import migrations, models


def cargar_ciclos_vida(apps, schema_editor):
    CicloVida = apps.get_model("parametro", "CicloVida")
    for descripcion in ("INFANCIA", "ADOLESCENCIA", "ADULTEZ", "ADULTO MAYOR"):
        CicloVida.objects.get_or_create(
            dsc_ciclo_vida=descripcion,
            defaults={"flg_activo": True},
        )


def limpiar_ciclos_vida(apps, schema_editor):
    CicloVida = apps.get_model("parametro", "CicloVida")
    CicloVida.objects.filter(
        dsc_ciclo_vida__in=["INFANCIA", "ADOLESCENCIA", "ADULTEZ", "ADULTO MAYOR"]
    ).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("parametro", "0003_paisprovincia_delete_paiszona_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="CicloVida",
            fields=[
                ("flg_activo", models.BooleanField(db_column="flg_activo", default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_column="created_at")),
                ("updated_at", models.DateTimeField(auto_now=True, db_column="updated_at")),
                (
                    "id_ciclo_vida",
                    models.AutoField(db_column="id_ciclo_vida", primary_key=True, serialize=False),
                ),
                ("dsc_ciclo_vida", models.CharField(db_column="dsc_ciclo_vida", max_length=150)),
            ],
            options={
                "verbose_name": "ciclo de vida",
                "verbose_name_plural": "ciclos de vida",
                "db_table": "ciclo_vida",
                "ordering": ("dsc_ciclo_vida", "id_ciclo_vida"),
            },
        ),
        migrations.RunPython(cargar_ciclos_vida, limpiar_ciclos_vida),
    ]
