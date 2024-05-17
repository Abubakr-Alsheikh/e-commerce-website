from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import (index, analyze_video, ask_question, video_list, video_details)

app_name = 'ask-yourtube'
urlpatterns = [
    path('', index, name='index'),
    path('analyze-video/', analyze_video, name='analyze-video'),
    path('ask-question/', ask_question, name='ask-question'),
    path('video-list/', video_list, name='video-list'),  
    path('video-details/<uuid:video_id>/', video_details, name='video-details'), 
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)