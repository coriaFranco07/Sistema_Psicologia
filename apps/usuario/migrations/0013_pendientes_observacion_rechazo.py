from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("usuario", "0012_pacientependiente"),
    ]

    operations = [
        migrations.AddField(
            model_name="pacientependiente",
            name="observacion_rechazo",
            field=models.TextField(blank=True, default=""),
        ),
        migrations.AddField(
            model_name="psicologopendiente",
            name="observacion_rechazo",
            field=models.TextField(blank=True, default=""),
        ),
    ]
