import apps.usuario.models
import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("parametro", "0004_ciclo_vida"),
    ]

    operations = [
        migrations.CreateModel(
            name="Psicologo",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nombres", models.CharField(max_length=100)),
                ("email", models.EmailField(max_length=50, unique=True)),
                (
                    "dni",
                    models.PositiveBigIntegerField(
                        unique=True,
                        validators=[
                            django.core.validators.MinValueValidator(1000000),
                            django.core.validators.MaxValueValidator(99999999),
                        ],
                    ),
                ),
                (
                    "cuil",
                    models.PositiveBigIntegerField(
                        blank=True,
                        null=True,
                        unique=True,
                        validators=[
                            django.core.validators.MinValueValidator(10000000000),
                            django.core.validators.MaxValueValidator(99999999999),
                        ],
                    ),
                ),
                ("fch_nacimiento", models.DateField(verbose_name="Fecha de nacimiento")),
                (
                    "foto",
                    models.FileField(
                        blank=True,
                        null=True,
                        upload_to="personas/fotos/",
                        validators=[
                            django.core.validators.FileExtensionValidator(["jpg", "jpeg", "png", "webp"]),
                            apps.usuario.models.validate_photo_size,
                        ],
                    ),
                ),
                ("fch_creacion", models.DateTimeField(auto_now_add=True)),
                ("fch_actualizacion", models.DateTimeField(auto_now=True)),
                (
                    "id_estado",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.RESTRICT,
                        related_name="%(class)ss",
                        to="parametro.estado",
                        verbose_name="Estado",
                    ),
                ),
            ],
            options={
                "verbose_name": "Psicologo",
                "verbose_name_plural": "Psicologos",
                "ordering": ("nombres", "dni"),
            },
        ),
        migrations.CreateModel(
            name="Paciente",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nombres", models.CharField(max_length=100)),
                ("email", models.EmailField(max_length=50, unique=True)),
                (
                    "dni",
                    models.PositiveBigIntegerField(
                        unique=True,
                        validators=[
                            django.core.validators.MinValueValidator(1000000),
                            django.core.validators.MaxValueValidator(99999999),
                        ],
                    ),
                ),
                (
                    "cuil",
                    models.PositiveBigIntegerField(
                        blank=True,
                        null=True,
                        unique=True,
                        validators=[
                            django.core.validators.MinValueValidator(10000000000),
                            django.core.validators.MaxValueValidator(99999999999),
                        ],
                    ),
                ),
                ("fch_nacimiento", models.DateField(verbose_name="Fecha de nacimiento")),
                (
                    "foto",
                    models.FileField(
                        blank=True,
                        null=True,
                        upload_to="personas/fotos/",
                        validators=[
                            django.core.validators.FileExtensionValidator(["jpg", "jpeg", "png", "webp"]),
                            apps.usuario.models.validate_photo_size,
                        ],
                    ),
                ),
                ("fch_creacion", models.DateTimeField(auto_now_add=True)),
                ("fch_actualizacion", models.DateTimeField(auto_now=True)),
                (
                    "id_ciclo_vida",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.RESTRICT,
                        related_name="pacientes",
                        to="parametro.ciclovida",
                        verbose_name="Ciclo de vida",
                    ),
                ),
                (
                    "id_estado",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.RESTRICT,
                        related_name="%(class)ss",
                        to="parametro.estado",
                        verbose_name="Estado",
                    ),
                ),
                (
                    "id_grado_estudio",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.RESTRICT,
                        related_name="pacientes",
                        to="parametro.gradoestudio",
                        verbose_name="Grado de estudio",
                    ),
                ),
                (
                    "id_ocupacion",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.RESTRICT,
                        related_name="pacientes",
                        to="parametro.ocupacion",
                        verbose_name="Ocupacion",
                    ),
                ),
            ],
            options={
                "verbose_name": "Paciente",
                "verbose_name_plural": "Pacientes",
                "ordering": ("nombres", "dni"),
            },
        ),
    ]
