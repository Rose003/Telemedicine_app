from django.urls import path,re_path
from . import views, consumers
from django.conf import settings
from django.conf.urls.static import static

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
    path('labs/', views.labs, name='labs'),  # Add this line

    re_path(r'ws/lab-updates/$', consumers.LabAnalysisConsumer.as_asgi()),

]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
