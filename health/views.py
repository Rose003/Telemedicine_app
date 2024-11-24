from django.shortcuts import render,redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect,csrf_exempt
from django.views.decorators.http import require_http_methods
from .utils import LabReportAnalyzer
from datetime import datetime
import json
from .ai_service import get_health_insights, get_chatbot_response, translate_text
from .forms import PatientRegistrationForm
from django.contrib import messages
from .models import Patients, Doctors, Admin, HealthLabreport, Appointments,Notification
from django.contrib.auth.hashers import make_password, check_password
from functools import wraps
import hashlib
import os
from django.conf import settings
from django.core.files.storage import default_storage
from django.utils import timezone
from django.core.files.base import ContentFile
from django.utils import timezone
import PyPDF2
from django.core.files.base import ContentFile
from collections import defaultdict
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Appointments, Patients, Doctors
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_date, parse_time
from datetime import datetime
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password
from django.db import IntegrityError
from datetime import timedelta
from django.utils import timezone
from django.templatetags.static import static




def home(request):
    return render(request, 'health/index.html')

def get_started(request):
    return render(request, 'health/plan.html')

def about(request):
    return render(request, 'health/about.html')


def patient_signup(request):
    if request.method == 'POST':
        print("Form submitted with data:", request.POST)  # Debug print
        try:
            patient = Patients(
                first_name=request.POST['first_name'],
                last_name=request.POST['last_name'],
                email=request.POST['email'],
                phone=request.POST['phone'],
                date_of_birth=request.POST['date_of_birth'],
                gender=request.POST['gender'],
                address=request.POST['address'],
                password_hash=make_password(request.POST['password_hash'])
            )
            patient.save()
            messages.success(request, 'Registration successful!')
            return redirect('login')
        except Exception as e:
            messages.error(request, f'Registration failed: {str(e)}')
            return render(request, 'health/authentication2.html')
    
    return render(request, 'health/authentication2.html')

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        print(f"Login attempt for: {email}")

        # Doctor Login
        try:
            doctor = Doctors.objects.get(email=email)
            print("Doctor account found")
            if check_password(password, doctor.password_hash):
                request.session['user_type'] = 'DOCTOR'
                request.session['user_id'] = doctor.doctor_id
                request.session['first_name'] = doctor.first_name
                 # Create notification for doctor login
                Notification.objects.create(
                    type='doctor_login',
                    message=f'Doctor {doctor.first_name} {doctor.last_name} logged in',
                    related_doctor=doctor
                )
                
                # Update last login time
                doctor.last_login = timezone.now()
                doctor.save()
                
                print("Doctor login successful")
                return redirect('doctor_dashboard')
            else:
                print("Invalid password for doctor account")
                messages.error(request, 'Invalid credentials')
                
        except Doctors.DoesNotExist:
            print("No doctor account found, checking patient accounts")

        # Patient Login
        try:
            patient = Patients.objects.get(email=email)
            print("Patient account found")
            if check_password(password, patient.password_hash):
                request.session['user_type'] = 'PATIENT'
                request.session['user_id'] = patient.patient_id
                request.session['first_name'] = patient.first_name
                print("Patient login successful")
                return redirect('patient_dashboard')
            else:
                print("Invalid password for patient account")
                messages.error(request, 'Invalid credentials')
                
        except Patients.DoesNotExist:
            print("No patient account found, checking admin accounts")

        # Admin Login
        try:
            admin = Admin.objects.get(email=email)
            print("Admin account found")
            hashed_password = hashlib.sha1(password.encode()).hexdigest()
            
            if admin.password_hash == hashed_password:
                request.session['user_type'] = 'ADMIN'
                request.session['user_id'] = admin.admin_id
                request.session['role'] = admin.role
                print("Admin login successful")
                # Update last login time
                admin.last_login = timezone.now()
                admin.save()
                return redirect('admin_dashboard')
            else:
                print("Invalid password for admin account")
                messages.error(request, 'Invalid credentials')
                
        except Admin.DoesNotExist:
            print("No admin account found")
            messages.error(request, 'Invalid credentials')

    return render(request, 'health/login.html')



def patient_portal(request):
    return render(request, 'health/authentication2.html')

def medication(request):
    return render(request, 'health/medication.html')
def contact(request):
    return render(request, 'health/contect.html')
def role(request):
    return render(request,'health/role.html')


def login_required(user_type):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if request.session.get('user_type') == user_type:
                return view_func(request, *args, **kwargs)
            return redirect('login')
        return wrapper
    return decorator

@login_required('ADMIN')
def admin_dashboard(request):
    admin = Admin.objects.get(admin_id=request.session.get('user_id'))
    doctors = Doctors.objects.all()
    patients = Patients.objects.all()
    appointments = Appointments.objects.all()
    appointments = Appointments.objects.select_related('patient', 'doctor').all()
    notifications = Notification.objects.all().order_by('-created_at')[:5]  # Get 5 most recent notifications
    unread_notifications_count = Notification.objects.filter(is_read=False).count()
    working_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    context = {
        'admin': admin,
        'doctors': doctors,
        'appointments': appointments,
        'doctors_count': doctors.count(),
        'patients_count': patients.count(),
        'appointments_count': appointments.count(),
        'notifications': notifications,
        'unread_notifications_count': unread_notifications_count,
        'working_days': working_days  



    }
    return render(request, 'health/admin_dashboard.html', context)

@login_required('ADMIN')
def update_admin_settings(request):
    if request.method == 'POST':
        try:
            admin = Admin.objects.get(admin_id=request.session.get('user_id'))
            
            # Update basic info
            admin.username = request.POST.get('username')
            admin.email = request.POST.get('email')
            
            # Handle password change
            current_password = request.POST.get('current_password')
            new_password = request.POST.get('new_password')
            if current_password and new_password:
                current_password_hash = hashlib.sha1(current_password.encode()).hexdigest()
                if current_password_hash == admin.password_hash:
                    admin.password_hash = hashlib.sha1(new_password.encode()).hexdigest()
                else:
                    return JsonResponse({
                        'success': False,
                        'message': 'Current password is incorrect'
                    })
            
            
            # Handle profile image
            if 'profile_image' in request.FILES:
                admin.profile_image = request.FILES['profile_image']
            
            admin.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Settings updated successfully'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

@require_http_methods(["POST"])
def add_doctor(request):
    try:
        # Process schedule data with default working hours
        schedule_data = {}
        working_days = request.POST.getlist('schedule[]')
        if not working_days:
            # Set default schedule if none selected
            working_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
            
        for day in working_days:
            schedule_data[day] = {
                "start": "09:00",
                "end": "17:00"
            }

        # Handle image upload
        image = request.FILES.get('image')
        
        # Create doctor object
        doctor = Doctors.objects.create(
            first_name=request.POST['first_name'],
            last_name=request.POST['last_name'],
            email=request.POST['email'],
            phone=request.POST['phone'],
            specialization=request.POST['specialization'],
            username=request.POST['username'],
            password_hash=make_password(request.POST['temp_password']),
            schedule=schedule_data,
            image=image,
            is_active=True,
            date_joined=timezone.now()
        )

        # Create notification
        Notification.objects.create(
            type='new_doctor',
            message=f'New doctor {doctor.first_name} {doctor.last_name} has been added',
            related_doctor=doctor
        )

        return JsonResponse({
            'success': True,
            'message': 'Doctor added successfully',
            'doctor_id': doctor.doctor_id
        })

    except Exception as e:
        print(f"Error adding doctor: {str(e)}")  # Add debugging
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required('DOCTOR')
def doctor_dashboard(request):
    doctor_id = request.session.get('user_id')
    
    try:
        doctor = Doctors.objects.get(doctor_id=doctor_id)
        
        # Get all appointments for this doctor
        all_appointments = Appointments.objects.filter(doctor_id=doctor_id)
        
        # Get pending appointments
        pending_appointments = all_appointments.filter(
            status='pending'
        ).order_by('appointment_date', 'appointment_time')
        
        # Get today's appointments
        today = timezone.now().date()
        todays_appointments = all_appointments.filter(
            appointment_date=today
        ).order_by('appointment_time')
        
        # Calculate statistics
        total_consultations = all_appointments.filter(status='completed').count()
        total_appointments = all_appointments.count()
        pending_reviews = all_appointments.filter(status='pending').count()
        
        # Get waiting list (upcoming appointments)
        waiting_list = all_appointments.filter(
            appointment_date__gte=today,
            status='confirmed'
        ).order_by('appointment_date', 'appointment_time')[:5]
        
        context = {
            'doctor': doctor,
            'pending_appointments': pending_appointments,
            'todays_appointments': todays_appointments,
            'total_consultations': total_consultations,
            'total_appointments': total_appointments,
            'pending_reviews': pending_reviews,
            'waiting_list': waiting_list,
            'consultation_trend': '+6.6%',  # You can calculate this based on historical data
            'appointment_trend': '-0.2%',   # You can calculate this based on historical data
            'rating': '4.8'                 # You can calculate this based on reviews
        }
        
        return render(request, 'health/doctor_dashboard.html', context)
        
    except Doctors.DoesNotExist:
        messages.error(request, 'Doctor account not found')
        return redirect('login')

    
@require_http_methods(["POST"])
def handle_appointment(request):
    data = json.loads(request.body)
    appointment_id = data.get('appointment_id')
    action = data.get('action')
    
    try:
        appointment = Appointments.objects.get(id=appointment_id)
        
        if action == 'confirm':
            appointment.status = 'confirmed'
        elif action == 'cancel':
            appointment.status = 'cancelled'
            
        appointment.updated_at = timezone.now()
        appointment.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Appointment {action}ed successfully'
        })
        
    except Appointments.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Appointment not found'
        }, status=404)

@require_http_methods(["POST"])
def update_appointment_status(request):
    data = json.loads(request.body)
    appointment_id = data.get('appointment_id')
    status = data.get('status')
    
    try:
        appointment = Appointments.objects.get(id=appointment_id)
        appointment.status = status
        appointment.updated_at = timezone.now()
        appointment.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Appointment {status} successfully'
        })
    except Appointments.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Appointment not found'
        }, status=404)

@require_http_methods(["DELETE"])
def delete_appointment(request):
    appointment_id = request.GET.get('id')
    
    try:
        appointment = Appointments.objects.get(id=appointment_id)
        appointment.delete()
        return JsonResponse({
            'success': True,
            'message': 'Appointment deleted successfully'
        })
    except Appointments.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Appointment not found'
        }, status=404)

@require_http_methods(["GET"])
def get_appointment_status(request):
    upcoming_appointments = Appointments.objects.filter(
        patient_id=request.session.get('user_id'),
        appointment_date__gte=timezone.now()
    ).select_related('doctor').values(
        'id', 'status', 'appointment_date', 'appointment_time',
        'doctor__first_name', 'doctor__last_name', 'doctor__specialization'
    )
    
    return JsonResponse({
        'appointments': list(upcoming_appointments)
    })




@login_required('PATIENT')
def patient_dashboard(request):
   
    # Get all reports ordered by newest first
    lab_reports = HealthLabreport.objects.all().order_by('-upload_date')
    print("Fetched reports:", lab_reports)  # Add this line for debugging

    # Get upcoming appointments for the logged-in patient
    upcoming_appointments = Appointments.objects.filter(
        patient_id=request.session.get('user_id'),
        appointment_date__gte=timezone.now(),
        status='pending'
    ).select_related('doctor').order_by('appointment_date')[:3]  # Limit to 3 most recent
    
    context = {
        'lab_reports': lab_reports,
        'first_name': request.session.get('first_name'),  # Add this line
        'upcoming_appointments': upcoming_appointments

    }
    return render(request, 'health/patient_dashboard.html', context)

def calculate_bmi(request):
    bmi_data = None
    error_message = None
    rotation_angle = 0

    if request.method == 'POST':
        weight = request.POST.get('weight')
        height = request.POST.get('height')
        sex = request.POST.get('sex')
        age = request.POST.get('age')
        waist = request.POST.get('waist', '')
        hip = request.POST.get('hip', '')

        if not (weight.isdigit() and height.isdigit() and age.isdigit() and
                (waist.isdigit() or not waist) and (hip.isdigit() or not hip)):
            error_message = 'Please enter valid numerical values for weight, height, age, waist, and hip.'
            return render(request, 'health/authentication.html', {'error': error_message})

        weight = float(weight)
        height = float(height)
        age = int(age)
        waist = float(waist) if waist else None
        hip = float(hip) if hip else None

        height_in_meters = height / 100
        bmi = weight / (height_in_meters ** 2)

        if bmi < 18.5:
            bmi_category = "Underweight"
            health_risk = "Low risk"
        elif 18.5 <= bmi < 24.9:
            bmi_category = "Normal weight"
            health_risk = "Average risk"
        elif 25 <= bmi < 29.9:
            bmi_category = "Overweight"
            health_risk = "Increased risk"
        else:
            bmi_category = "Obesity"
            health_risk = "High risk"

        rotation_angle = (bmi / 40) * 360 if bmi else 0

        ideal_weight_lower = 18.5 * (height_in_meters ** 2)
        ideal_weight_upper = 24.9 * (height_in_meters ** 2)
        surface_area = 0.007184 * (weight ** 0.425) * (height ** 0.725)
        ponderal_index = weight / (height_in_meters ** 3)

        if sex.lower() == 'male':
            bmr = 10 * weight + 6.25 * height - 5 * age + 5
        else:
            bmr = 10 * weight + 6.25 * height - 5 * age - 161

        whr = waist / hip if waist and hip else None
        whr_status = "Healthy" if whr and whr < 0.85 else "At risk" if whr else None

        whtr = waist / height if waist else None
        whtr_status = "Healthy" if whtr and whtr < 0.5 else "At risk" if whtr else None

        bmi_data = {
            'bmi': {'value': round(bmi, 2), 'status': bmi_category, 'risk': health_risk, 'prime': 22.5},
            'ideal_weight': {'lower': round(ideal_weight_lower, 2), 'upper': round(ideal_weight_upper, 2)},
            'surface_area': round(surface_area, 2),
            'ponderal_index': round(ponderal_index, 2),
            'bmr': {'value': round(bmr, 2)},
            'whr': {'value': round(whr, 2) if whr else None, 'status': whr_status},
            'whtr': {'value': round(whtr, 2) if whtr else None, 'status': whtr_status},
            'waist': waist,
            'hip': hip
        }

        # Get health insights based on calculated BMI
        health_insights = get_health_insights(round(bmi, 2))
        bmi_data['health_insights'] = health_insights


        return render(request, 'health/patient_dashboard.html', {'bmi_data': bmi_data, 'rotation_angle': rotation_angle})

    return render(request, 'health/patient_dashboard.html')

@require_http_methods(["POST"])
def get_health_insights_view(request):
    try:
        data = json.loads(request.body)
        bmi = data.get('bmi')
        
        if bmi:
            insights = get_health_insights(bmi)
            return JsonResponse(insights)
        else:
            return JsonResponse({'error': 'BMI value is required'}, status=400)
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def extract_text_from_pdf(file_path):
    text = ""
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text()
    return text

from django.shortcuts import render
from .utils import LabReportAnalyzer
import PyPDF2
from .models import HealthLabreport
from django.http import JsonResponse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.utils import timezone
import os
from django.conf import settings

def labs(request):
    analyzer = LabReportAnalyzer()
    lab_reports = HealthLabreport.objects.all().order_by('-upload_date')
    
    analyzed_data = {}
    
    for report in lab_reports:
        file_path = os.path.join(settings.MEDIA_ROOT, str(report.file_path))
        text = extract_text_from_pdf(file_path)
        
        # Use analyze_with_ai instead of extract_lab_values
        analysis = analyzer.analyze_with_ai(text)
        analyzed_data[str(report.id)] = analysis
        print(f"Analysis for report {report.id}: {analyzed_data[str(report.id)]}")  # Debug print
    
    context = {
        'lab_reports': lab_reports,
        'analyzed_data': analyzed_data
    }
    
    return render(request, 'health/labs.html', context)



def upload_lab_report(request):
    if request.method == 'POST':
        file = request.FILES.get('lab_report')
        hospital = request.POST.get('hospital')
        
        if file and hospital:
            upload_dir = os.path.join(settings.MEDIA_ROOT, 'lab_reports')
            os.makedirs(upload_dir, exist_ok=True)
            
            file_path = os.path.join('lab_reports', file.name)
            path = default_storage.save(file_path, ContentFile(file.read()))
            
            report = HealthLabreport.objects.create(
                filename=file.name,
                file_path=path,
                hospital=hospital,
                upload_date=timezone.now()
            )
            
            analyzer = LabReportAnalyzer()
            text = extract_text_from_pdf(os.path.join(settings.MEDIA_ROOT, path))
            analysis = analyzer.analyze_with_ai(text)

            # Store analysis results in the report object
            report.analysis_results = json.dumps(analysis)
            report.save()       
            return JsonResponse({
                'success': True,
                'id': report.id,
                'filename': report.filename,
                'file_url': f'/media/{report.file_path}',
                'hospital': report.hospital,
                'date': report.upload_date.strftime('%Y-%m-%d'),
                'analysis': analysis
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@csrf_exempt
@require_http_methods(["DELETE"])
def delete_report(request, report_id):
    try:
        report = HealthLabreport.objects.get(id=report_id)
        # Delete the report
        report.delete()
        return JsonResponse({'success': True})
    except HealthLabreport.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Report not found'}, status=404)



@require_http_methods(["POST"])
def chatbot_response(request):
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '')
        
        # Get response from chatbot API
        bot_response = get_chatbot_response(user_message)
        
        return JsonResponse({
            'message': bot_response['response'],
            'timestamp': datetime.now().strftime("%H:%M")
        })
    except Exception as e:
        return JsonResponse({
            'message': "I'm here to help with your health questions. What would you like to know?",
            'timestamp': datetime.now().strftime("%H:%M")
        })



def translate_content(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        text = data.get('text')
        target_lang = data.get('target', 'sw')
        
        translated_text = translate_text(text, target_lang)
        return JsonResponse({'translated': translated_text})
    
def doctors(request):
    doctors = Doctors.objects.all()
    doctor_list = []
    doctors_count = Doctors.objects.count()
    
    for doctor in doctors:
        doctor_data = {
            'id': doctor.doctor_id,
            'name': f"{doctor.first_name} {doctor.last_name}",
            'specialization': doctor.specialization,
            'image': doctor.image.url if doctor.image else static('health/images/doctor1.png'),  # Correct static fallback
            'email': doctor.email,
            'phone': doctor.phone,
            'schedule': doctor.schedule
        }
        doctor_list.append(doctor_data)
    
    context = {
        'doctors': doctor_list,
        'doctors_count': doctors_count
    }
    return render(request, 'health/doctors.html', context)

def extract_text_from_pdf(file_path):
    text = ""
    try:
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text()
    except Exception as e:
        print(f"PDF Extraction Log: {str(e)}")
        text = "Unable to extract text from PDF"
    return text


def parse_date(date_string):
    try:
        return datetime.strptime(date_string, '%Y-%m-%d').date()
    except ValueError:
        return None

def parse_time(time_string):
    try:
        return datetime.strptime(time_string, '%H:%M').time()
    except ValueError:
        return None

def book_appointment(request):
    if request.method == 'POST':
        try:
            appointment = Appointments.objects.create(
                patient_id=request.POST.get('patient_id'),
                doctor_id=request.POST.get('doctor_id'),
                appointment_date=request.POST.get('appointment_date'),
                appointment_time=request.POST.get('appointment_time'),
                status='pending',  # This matches your STATUS_CHOICES
                created_at=timezone.now(),
                updated_at=timezone.now()
            )
            # Create notification for new appointment
            Notification.objects.create(
                type='new_appointment',
                message=f'New appointment booked for patient ID {appointment.patient_id} with Doctor ID {appointment.doctor_id}',
                related_appointment=appointment
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Appointment booked successfully',
                'appointment_id': appointment.id
            })
            
        except Exception as e:
            print(f"Appointment creation error: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
        
@require_http_methods(["DELETE"])
def delete_doctor(request, doctor_id):
    try:
        doctor = Doctors.objects.get(doctor_id=doctor_id)
        doctor.delete()
        
        # Create notification for doctor deletion
        Notification.objects.create(
            type='doctor_deleted',
            message=f'Doctor {doctor.first_name} {doctor.last_name} has been removed from the system'
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Doctor deleted successfully'
        })
    except Doctors.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Doctor not found'
        }, status=404)

import http.client
import json
from django.http import JsonResponse

@csrf_exempt
@require_http_methods(["POST"])
def send_contact_email(request):
    if request.method == 'POST':
        # Get form data with default values
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        subject = request.POST.get('subject', 'New Contact Inquiry')
        message = request.POST.get('message', '')
        
        conn = http.client.HTTPSConnection("mail-sender-api1.p.rapidapi.com")
        
        
        # Format the payload as a raw string
        payload = f"""{{
            "sendto": "okemwaroselyn@gmail.com",
            "name": "user2024",
            "replyTo": "admin@go-mail.us.to",
            "ishtml": "false",
            "title": "{subject}",
            "body": "from: {name}\\nEmail: {email}\\n\\nMessage:\\n{message}"
        }}"""
        
        headers = {
        'x-rapidapi-key': "84ab80797emsh4b2b532eb8764b7p19fb6fjsn3bef2a7e0c71",
            'x-rapidapi-host': "mail-sender-api1.p.rapidapi.com",
            'Content-Type': "application/json"
        }
        
        conn.request("POST", "/", payload, headers)
        res = conn.getresponse()
        data = res.read()
        
        return JsonResponse({'success': True, 'response': data.decode("utf-8")})
    
    return JsonResponse({'success': False})
