# Generated by Django 4.2.2 on 2023-06-18 15:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pointme', '0005_etudiantscan'),
    ]

    operations = [
        migrations.RenameField(
            model_name='etudiantscan',
            old_name='telephone_qr_code',
            new_name='telephone',
        ),
    ]
