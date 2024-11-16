# Generated by Django 5.1.2 on 2024-11-11 14:39

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Patients',
            fields=[
                ('patient_id', models.AutoField(primary_key=True, serialize=False)),
                ('first_name', models.CharField(max_length=45)),
                ('last_name', models.CharField(max_length=45)),
                ('email', models.CharField(max_length=45, unique=True)),
                ('password_hash', models.CharField(blank=True, max_length=255, null=True)),
                ('phone', models.IntegerField()),
                ('date_of_birth', models.DateField()),
                ('gender', models.CharField(max_length=6)),
                ('address', models.CharField(max_length=45)),
            ],
            options={
                'db_table': 'patients',
                'managed': False,
            },
        ),
    ]
