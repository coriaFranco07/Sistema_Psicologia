from django.db import migrations


LEGACY_TO_CURRENT = {
    "ADULTEZ": "ADULTEZ INICIAL",
    "ADULTO MAYOR": "VEJEZ",
}
REQUIRED_CICLOS_VIDA = (
    "INFANCIA",
    "ADOLESCENCIA",
    "ADULTEZ INICIAL",
    "ADULTEZ MADURA",
    "VEJEZ",
)


def actualizar_ciclos_vida(apps, schema_editor):
    CicloVida = apps.get_model("parametro", "CicloVida")

    for descripcion in REQUIRED_CICLOS_VIDA:
        ciclo_vida, _ = CicloVida.objects.get_or_create(
            dsc_ciclo_vida=descripcion,
            defaults={"flg_activo": True},
        )
        if not ciclo_vida.flg_activo:
            ciclo_vida.flg_activo = True
            ciclo_vida.save(update_fields=["flg_activo"])

    for descripcion_legacy, descripcion_actual in LEGACY_TO_CURRENT.items():
        ciclo_vida_actual = (
            CicloVida.objects.filter(dsc_ciclo_vida=descripcion_actual).order_by("id_ciclo_vida").first()
        )
        ciclo_vida_legacy = (
            CicloVida.objects.filter(dsc_ciclo_vida=descripcion_legacy).order_by("id_ciclo_vida").first()
        )

        if ciclo_vida_actual is None and ciclo_vida_legacy is not None:
            ciclo_vida_legacy.dsc_ciclo_vida = descripcion_actual
            ciclo_vida_legacy.flg_activo = True
            ciclo_vida_legacy.save(update_fields=["dsc_ciclo_vida", "flg_activo"])
            continue

        if ciclo_vida_legacy is not None and ciclo_vida_actual is not None:
            ciclo_vida_legacy.flg_activo = False
            ciclo_vida_legacy.save(update_fields=["flg_activo"])


class Migration(migrations.Migration):
    dependencies = [
        ("parametro", "0005_rama"),
    ]

    operations = [
        migrations.RunPython(actualizar_ciclos_vida, migrations.RunPython.noop),
    ]
