from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0012_one_apikey_per_user'),
    ]

    operations = [
        migrations.RenameField(
            model_name='job',
            old_name='invalid_molecules',
            new_name='invalid_rows',
        ),
    ]
