# Generated by Django 4.2.2 on 2023-06-28 16:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pointme', '0012_alter_etudiant_qr_code_data'),
    ]

    operations = [
        migrations.AlterField(
            model_name='etudiant',
            name='qr_code_data',
            field=models.CharField(blank=True, default=dict, max_length=200),
        ),
    ]
