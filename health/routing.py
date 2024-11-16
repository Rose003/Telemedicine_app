from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'health/ws/lab-updates/$', consumers.LabAnalysisConsumer.as_asgi()),
]
