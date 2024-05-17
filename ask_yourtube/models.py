from django.db import models
from django.contrib.auth.models import User
import uuid 
    
class Video(models.Model):
    user_id = models.UUIDField(primary_key=True)
    youtube_title = models.CharField(max_length=300)
    youtube_link = models.URLField(unique=True)  
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.youtube_title

class VideoSession(models.Model):
    session_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    video = models.ForeignKey(Video, on_delete=models.CASCADE) 
    transcript = models.TextField(blank=True)
    summary = models.TextField(blank=True)
    chat_history = models.JSONField(default=list, blank=True) 
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Session ID: {self.session_id} for Video: {self.video.youtube_title}"