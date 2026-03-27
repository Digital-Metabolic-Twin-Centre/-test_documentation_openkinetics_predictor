from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0014_job_kcat_km_method_and_prediction_type_length"),
    ]

    operations = [
        migrations.AddField(
            model_name="job",
            name="canonicalize_substrates",
            field=models.BooleanField(default=True),
        ),
    ]
