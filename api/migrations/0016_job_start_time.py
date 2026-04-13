from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0015_job_canonicalize_substrates"),
    ]

    operations = [
        migrations.AddField(
            model_name="job",
            name="start_time",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
