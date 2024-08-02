from datetime import time
import os
from django.conf import settings
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from .models import Task, ChatHistory
from .serializers import TaskSerializer
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserSerializer, ChatHistorySerializer
import google.generativeai as genai


class SignupView(CreateAPIView):
    queryset = get_user_model().objects.all()
    permission_classes = [AllowAny]
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Generate tokens for the new user
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token

        data = {
            "user": serializer.data,
            "refresh": str(refresh),
            "access": str(access_token),
        }
        return Response(data, status=status.HTTP_201_CREATED)


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]  # Require authentication

    def get_queryset(self):
        """Return tasks for the currently authenticated user."""
        return Task.objects.filter(user=self.request.user)

    def create(self, request):
        """Create a new task for the authenticated user."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Get the current user from the request
        user = request.user

        # Add the user to the task data
        serializer.save(user=user)

        return Response(serializer.data, status=201)

    def update(self, request, pk=None):
        """Update a task (only for the task owner)."""
        task = self.get_object()
        if task.user != request.user:
            return Response(
                {"detail": "You do not have permission to perform this action."},
                status=403,
            )
        serializer = self.get_serializer(
            task, data=request.data, partial=True
        )  # Allow partial updates
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def destroy(self, request, pk=None):
        """Delete a task (only for the task owner)."""
        task = self.get_object()
        if task.user != request.user:
            return Response(
                {"detail": "You do not have permission to perform this action."},
                status=403,
            )
        task.delete()
        return Response(status=204)  # 204 No Content


genai.configure(api_key=settings.GENAI_API_KEY)

generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
)


def upload_to_gemini(path, display_name=None, mime_type=None):
    """Uploads the given file to Gemini.

    See https://ai.google.dev/gemini-api/docs/prompting_with_media
    """
    file = genai.upload_file(path, display_name=display_name, mime_type=mime_type)
    print(f"Uploaded file '{file.display_name}' as: {file.uri}")
    return file


class ChatHistoryViewSet(viewsets.ModelViewSet):
    serializer_class = ChatHistorySerializer
    permission_classes = [permissions.IsAuthenticated]
    # parser_classes = [MultiPartParser, FormParser] # For handling file uploads
    # parser_classes = (MultiPartParser, FormParser)

    def get_queryset(self):
        """Return the chat history for the currently authenticated user."""
        return ChatHistory.objects.filter(user=self.request.user)

    def create(self, request):
        user = request.user
        chat_history, created = ChatHistory.objects.get_or_create(user=user)
        new_message = {
            "role": "user",
            "parts": [],
        }

        uploaded_file = request.FILES.get("file")  # Get the uploaded file
        if uploaded_file:
            # File upload logic
            file_path = os.path.join(settings.MEDIA_ROOT, uploaded_file.name)
            with open(file_path, "wb+") as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)

            # Upload to Gemini
            try:
                gemini_file = upload_to_gemini(file_path, uploaded_file.content_type)
                new_message["parts"].append(gemini_file)
                # new_message["parts"].append(file_path)
            except Exception as e:
                return Response(
                    {"error": f"Failed to upload file to Gemini: {str(e)}"}, status=500
                )
            finally:
                # Optionally delete the file after uploading to Gemini
                os.remove(file_path)

        user_message = request.data.get("content")
        if user_message:
            new_message["parts"].append(user_message)

        if new_message["parts"]:  # Check if the message has any content (file or text)

            # Prepare history for Gemini
            gemini_history = chat_history.current_chat

            # Start a new chat session if the history is empty
            if not gemini_history:
                chat_session = model.start_chat()
            else:
                chat_session = model.start_chat(history=gemini_history)
            if user_message:
                response = chat_session.send_message(new_message["parts"])
                response = response.text
                # response = user_message

                # Add AI response to chat history
                ai_message = {
                    "role": "model",
                    "parts": [response],
                }  # Using 'parts' for consistency
                if uploaded_file != None:
                    new_message["parts"][0] = uploaded_file.name
                chat_history.current_chat.append(new_message)
                chat_history.current_chat.append(ai_message)
            chat_history.save()

            return Response(response, status=201)
        else:
            return Response({"error": "Message cannot be empty."}, status=400)

    @action(
        detail=False, methods=["POST"], url_path="clear"
    )  # Use detail=True for actions on a specific instance
    def clear_chat_history(self, request, pk=None):
        user = request.user  # Get the authenticated user
        chat_history, created = ChatHistory.objects.get_or_create(user=user)
        chat_history.clear_current_chat()
        return Response({"detail": "Chat history cleared successfully."})

    def update(self, request, pk=None):
        """Update a chat history (not typically used for chat)."""
        # You might not need this method,
        # but it's here for completeness in case you have
        # specific update logic for the entire chat history.
        chat_history = self.get_object()
        if chat_history.user != request.user:
            return Response(
                {"detail": "You do not have permission to perform this action."},
                status=403,
            )

        serializer = self.get_serializer(chat_history, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def destroy(self, request, pk=None):
        """Delete a chat history (only for the chat history owner)."""
        chat_history = self.get_object()
        if chat_history.user != request.user:
            return Response(
                {"detail": "You do not have permission to perform this action."},
                status=403,
            )
        chat_history.delete()
        return Response(status=204)
