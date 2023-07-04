# Generated by Django 4.2.2 on 2023-06-22 21:44

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('pointme', '0009_etudiant_date_scan_etudiant_heure_scan_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='EtudiantScan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_scan', models.DateField(default=django.utils.timezone.now)),
                ('heure_scan', models.TimeField(default=django.utils.timezone.now)),
                ('etudiant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pointme.etudiant')),
            ],
        ),
    ]
