import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("parametro", "0004_ciclo_vida"),
        ("usuario", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="DatosPersonales",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("telefono", models.CharField(max_length=25)),
                ("domicilio", models.CharField(max_length=200)),
                ("fch_creacion", models.DateTimeField(auto_now_add=True)),
                ("fch_actualizacion", models.DateTimeField(auto_now=True)),
                (
                    "id_localidad",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.RESTRICT,
                        to="parametro.localidad",
                        verbose_name="Localidad",
                    ),
                ),
                (
                    "id_pais",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.RESTRICT,
                        to="parametro.pais",
                        verbose_name="Pais",
                    ),
                ),
                (
                    "id_provincia",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.RESTRICT,
                        to="parametro.provincia",
                        verbose_name="Provincia",
                    ),
                ),
                (
                    "id_sexo",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.RESTRICT,
                        to="parametro.sexo",
                        verbose_name="Sexo",
                    ),
                ),
                (
                    "id_std_civil",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.RESTRICT,
                        to="parametro.tipocivil",
                        verbose_name="Estado civil",
                    ),
                ),
                (
                    "id_zona",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.RESTRICT,
                        to="parametro.zona",
                        verbose_name="Zona",
                    ),
                ),
                (
                    "paciente",
                    models.OneToOneField(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="datos_personales",
                        to="usuario.paciente",
                    ),
                ),
                (
                    "psicologo",
                    models.OneToOneField(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="datos_personales",
                        to="usuario.psicologo",
                    ),
                ),
            ],
            options={
                "verbose_name": "Dato personal",
                "verbose_name_plural": "Datos personales",
                "ordering": ("-fch_actualizacion",),
            },
        ),
        migrations.AddConstraint(
            model_name="datospersonales",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    models.Q(("psicologo__isnull", False), ("paciente__isnull", True)),
                    models.Q(("psicologo__isnull", True), ("paciente__isnull", False)),
                    _connector="OR",
                ),
                name="datos_personales_una_sola_persona",
            ),
        ),
    ]
