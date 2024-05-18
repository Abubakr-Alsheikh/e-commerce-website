
from django.db import models
import uuid


class UserCustom(models.Model):
    user_id = models.UUIDField(primary_key=True)
    # Add other user-related fields here
    # ...

    def __str__(self):
        return str(self.user_id)  # Or any other representation you prefer

class Video(models.Model):
    user_id =  models.ForeignKey(UserCustom, on_delete=models.CASCADE, null=True, blank=True)  # Foreign key to User
    video_title = models.CharField(max_length=300)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.video_title

class VideoSession(models.Model):
    session_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    transcript = models.TextField(blank=True)
    summary = models.TextField(blank=True)
    chat_history = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Session ID: {self.session_id} for Video: {self.video.video_title}"