from django.db import models
from django.contrib.auth.models import User
from django.core.serializers.json import DjangoJSONEncoder
import json


class Task(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)  # Allow blank descriptions
    is_completed = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    parent_task = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="subtasks"
    )

    def __str__(self):
        return self.title


class ChatHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    full_history = models.JSONField(
        encoder=DjangoJSONEncoder, default=list
    )  # Stores complete chat as JSON
    current_chat = models.JSONField(
        encoder=DjangoJSONEncoder, default=list
    )  # Stores ongoing chat

    def clear_current_chat(self):
        """Clears the current chat and appends it to the full history."""
        self.full_history.extend(self.current_chat)
        self.current_chat = []
        self.save()

    def __str__(self):
        return f"Chat History for {self.user.username}"
