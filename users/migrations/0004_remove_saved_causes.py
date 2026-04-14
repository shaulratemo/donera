# Generated migration to remove saved_causes field

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_backfill_user_profiles'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='saved_causes',
        ),
    ]
