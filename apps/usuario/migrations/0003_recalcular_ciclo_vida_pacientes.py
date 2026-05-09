from django.db import migrations


def calculate_age_from_birth_date(fch_nacimiento, today):
    return today.year - fch_nacimiento.year - (
        (today.month, today.day) < (fch_nacimiento.month, fch_nacimiento.day)
    )


def get_ciclo_vida_descripcion_by_age(edad):
    if edad < 11:
        return "INFANCIA"
    if edad < 18:
        return "ADOLESCENCIA"
    if edad < 40:
        return "ADULTEZ INICIAL"
    if edad < 60:
        return "ADULTEZ MADURA"
    return "VEJEZ"


def recalcular_ciclo_vida_pacientes(apps, schema_editor):
    CicloVida = apps.get_model("parametro", "CicloVida")
    Paciente = apps.get_model("usuario", "Paciente")

    from datetime import date

    today = date.today()
    ciclos_vida = {
        ciclo_vida.dsc_ciclo_vida.upper(): ciclo_vida
        for ciclo_vida in CicloVida.objects.filter(flg_activo=True)
    }

    for paciente in Paciente.objects.all():
        if not paciente.fch_nacimiento:
            continue

        edad = calculate_age_from_birth_date(paciente.fch_nacimiento, today)
        descripcion = get_ciclo_vida_descripcion_by_age(edad)
        ciclo_vida = ciclos_vida.get(descripcion)
        if ciclo_vida is None:
            continue

        if paciente.id_ciclo_vida_id != ciclo_vida.pk:
            paciente.id_ciclo_vida_id = ciclo_vida.pk
            paciente.save(update_fields=["id_ciclo_vida"])


class Migration(migrations.Migration):
    dependencies = [
        ("parametro", "0006_actualizar_ciclos_vida"),
        ("usuario", "0002_psicologo_id_rama"),
    ]

    operations = [
        migrations.RunPython(recalcular_ciclo_vida_pacientes, migrations.RunPython.noop),
    ]
