from django.db import models
from django.contrib.auth.models import AbstractUser


class Patients(models.Model):
    patient_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=45)
    last_name = models.CharField(max_length=45)
    email = models.CharField(unique=True, max_length=45)
    password_hash = models.CharField(max_length=255, blank=True, null=True)
    phone = models.IntegerField()
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=6)
    address = models.CharField(max_length=45)

    class Meta:
        managed = False
        db_table = 'patients'


class HealthLabreport(models.Model):
    filename = models.CharField(max_length=255)
    file_path = models.FileField(upload_to='lab_reports/')
    hospital = models.CharField(max_length=255)
    upload_date = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ['-upload_date']


class Doctors(models.Model):
    doctor_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=45)
    last_name = models.CharField(max_length=45)
    specialization = models.CharField(max_length=45)
    email = models.CharField(unique=True, max_length=45)
    phone = models.IntegerField()
    schedule = models.JSONField()
    image = models.ImageField(upload_to='doctor_images/', null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'doctors'

class Admin(models.Model):
    admin_id = models.AutoField(primary_key=True)
    email = models.CharField(unique=True, max_length=45)
    password_hash = models.CharField(max_length=45)
    role = models.CharField(max_length=5)

    class Meta:
        managed = False
        db_table = 'admin'

class User(AbstractUser):
    USER_TYPES = (
        ('ADMIN', 'Admin'),
        ('DOCTOR', 'Doctor'),
        ('PATIENT', 'Patient')
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPES)
    email = models.EmailField(unique=True)

    class Meta:
        permissions = [
            ("can_view_patient", "Can view patient"),
            ("can_view_doctor", "Can view doctor"),
        ]

    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='health_users'
    )

    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='health_users'
    )
