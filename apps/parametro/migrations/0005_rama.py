from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("parametro", "0004_ciclo_vida"),
    ]

    operations = [
        migrations.CreateModel(
            name="Rama",
            fields=[
                ("flg_activo", models.BooleanField(db_column="flg_activo", default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_column="created_at")),
                ("updated_at", models.DateTimeField(auto_now=True, db_column="updated_at")),
                (
                    "id_rama",
                    models.AutoField(db_column="id_rama", primary_key=True, serialize=False),
                ),
                ("dsc_rama", models.CharField(db_column="dsc_rama", max_length=150)),
            ],
            options={
                "verbose_name": "rama",
                "verbose_name_plural": "ramas",
                "db_table": "rama",
                "ordering": ("dsc_rama", "id_rama"),
            },
        ),
    ]
