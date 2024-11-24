# Generated by Django 5.1.3 on 2024-11-24 12:33

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('health', '0004_alter_admin_profile_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClinicAdmin',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('facility_name', models.CharField(max_length=200)),
                ('facility_type', models.CharField(choices=[('HOSPITAL', 'Hospital'), ('CLINIC', 'Clinic'), ('LABORATORY', 'Laboratory'), ('PHARMACY', 'Pharmacy')], max_length=100)),
                ('facility_id', models.CharField(editable=False, max_length=10, unique=True)),
                ('verification_status', models.CharField(default='pending', max_length=20)),
                ('documents', models.FileField(upload_to='clinic_documents/')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='health.user')),
            ],
        ),
        migrations.CreateModel(
            name='HealthProfessional',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('specialization', models.CharField(max_length=100)),
                ('license_number', models.CharField(max_length=100)),
                ('verification_status', models.CharField(default='pending', max_length=20)),
                ('medical_license', models.FileField(upload_to='medical_documents/')),
                ('professional_id', models.CharField(editable=False, max_length=10, unique=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='health.user')),
            ],
        ),
    ]
