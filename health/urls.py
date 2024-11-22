from django.urls import path,re_path
from . import views, consumers
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin


urlpatterns = [
    # Your existing URL patterns
    path('', views.home, name='home'),
    path('patient-portal/', views.patient_portal, name='patient_portal'),
    path('calculate_bmi/', views.calculate_bmi, name='calculate_bmi'),
    path('get-health-insights/', views.get_health_insights, name='get_health_insights'),
    path('chatbot-response/', views.chatbot_response, name='chatbot_response'),
    path('translate/', views.translate_content, name='translate_content'),
    path('doctors/', views.doctors, name='doctors'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('doctor-dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('patient-dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path('upload-lab-report/', views.upload_lab_report, name='upload_lab_report'),
    path('delete-report/<int:report_id>/', views.delete_report, name='delete_report'),
    path('labs/', views.labs, name='labs'), 
    path('get_started/signup/', views.patient_signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('medication/', views.medication, name='medication'),
    path('api/book-appointment/', views.book_appointment, name='book_appointment'),
    path('api/handle-appointment/', views.handle_appointment, name='handle_appointment'),
    path('add-doctor/', views.add_doctor, name='add_doctor'),
    path('api/appointment/update-status/', views.update_appointment_status, name='update_appointment_status'),
    path('api/appointment/delete/', views.delete_appointment, name='delete_appointment'),
    path('api/appointments/status/', views.get_appointment_status, name='appointment_status'),
    path('get_started/', views.get_started, name='get_started'),
    path('about/', views.about, name='about'),
    path('update-admin-settings/', views.update_admin_settings, name='update_admin_settings'),




    re_path(r'ws/lab-updates/$', consumers.LabAnalysisConsumer.as_asgi()),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
