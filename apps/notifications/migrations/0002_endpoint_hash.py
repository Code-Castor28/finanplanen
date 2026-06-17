import hashlib

from django.db import migrations, models


def backfill_endpoint_hash(apps, schema_editor):
    SuscripcionPush = apps.get_model('notifications', 'SuscripcionPush')
    for obj in SuscripcionPush.objects.iterator():
        obj.endpoint_hash = hashlib.sha256(obj.endpoint.encode()).hexdigest()
        obj.save(update_fields=['endpoint_hash'])


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='suscripcionpush',
            name='endpoint',
            field=models.TextField(),
        ),
        migrations.AddField(
            model_name='suscripcionpush',
            name='endpoint_hash',
            field=models.CharField(max_length=64, null=True),
        ),
        migrations.RunPython(
            backfill_endpoint_hash,
            reverse_code=migrations.RunPython.noop,
        ),
        migrations.AlterField(
            model_name='suscripcionpush',
            name='endpoint_hash',
            field=models.CharField(max_length=64, unique=True),
        ),
    ]
