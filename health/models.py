from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.db import models
from django.core.exceptions import ValidationError
from datetime import datetime


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
        managed = True
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
    
    # New fields
    username = models.CharField(max_length=45, unique=True)
    password_hash = models.CharField(max_length=128)
    password_expiry = models.DateTimeField(null=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True)
    is_active = models.BooleanField(default=True) 
    class Meta:
        managed = True
        db_table = 'doctors'


class Admin(models.Model):
    admin_id = models.AutoField(primary_key=True)
    email = models.CharField(unique=True, max_length=45)
    password_hash = models.CharField(max_length=45)
    role = models.CharField(max_length=5)
    username = models.CharField(max_length=45, default='admin')
    profile_image = models.ImageField(upload_to='admin_profiles/', null=True, blank=True, default='doctor1.png')
    last_login = models.DateTimeField(null=True, blank=True)


    class Meta:
        managed = True
        db_table = 'admin'


class User(AbstractUser):
    USER_TYPES = (
        ('ADMIN', 'Admin'),
        ('DOCTOR', 'Doctor'),
        ('PATIENT', 'Patient'),
        ('CLINIC_ADMIN', 'Clinic Administrator'),
        ('HEALTH_PROFESSIONAL', 'Healthcare Professional'),
    )
    user_type = models.CharField(max_length=25, choices=USER_TYPES)
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

class Appointments(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]
    patient = models.ForeignKey('Patients', models.DO_NOTHING)
    doctor = models.ForeignKey('Doctors', models.DO_NOTHING)
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    status = models.CharField(max_length=9, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'appointments'

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('doctor_login', 'Doctor Login'),
        ('new_appointment', 'New Appointment'),
    ]
    
    type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    related_doctor = models.ForeignKey(Doctors, on_delete=models.CASCADE, null=True, blank=True)
    related_appointment = models.ForeignKey(Appointments, on_delete=models.CASCADE, null=True, blank=True)

class ClinicAdmin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    facility_name = models.CharField(max_length=200)
    facility_type = models.CharField(max_length=100, choices=[
        ('HOSPITAL', 'Hospital'),
        ('CLINIC', 'Clinic'),
        ('LABORATORY', 'Laboratory'),
        ('PHARMACY', 'Pharmacy')
    ])
    facility_id = models.CharField(max_length=10, unique=True, editable=False)
    verification_status = models.CharField(max_length=20, default='pending')
    documents = models.FileField(upload_to='clinic_documents/')

    def save(self, *args, **kwargs):
        if not self.facility_id:
            prefix = self.facility_type[:3].upper()
            last_facility = ClinicAdmin.objects.filter(
                facility_id__startswith=prefix
            ).order_by('-facility_id').first()
            
            if last_facility:
                last_number = int(last_facility.facility_id[3:])
                new_number = last_number + 1
            else:
                new_number = 1
                
            self.facility_id = f"{prefix}{new_number:03d}"
        super().save(*args, **kwargs)

class HealthProfessional(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    specialization = models.CharField(max_length=100)
    license_number = models.CharField(max_length=100)
    verification_status = models.CharField(max_length=20, default='pending')
    medical_license = models.FileField(upload_to='medical_documents/')
    professional_id = models.CharField(max_length=10, unique=True, editable=False)

    def save(self, *args, **kwargs):
        if not self.professional_id:
            prefix = 'HP'
            last_professional = HealthProfessional.objects.order_by('-professional_id').first()
            
            if last_professional:
                last_number = int(last_professional.professional_id[2:])
                new_number = last_number + 1
            else:
                new_number = 1
                
            self.professional_id = f"{prefix}{new_number:03d}"
        super().save(*args, **kwargs)


