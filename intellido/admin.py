from django.contrib import admin
from .models import Task, ChatHistory

# Register your models here.
admin.site.register(Task)
admin.site.register(ChatHistory)
