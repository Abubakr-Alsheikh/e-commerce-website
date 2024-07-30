from rest_framework import viewsets, permissions
from rest_framework.response import Response
from .models import Task
from .serializers import TaskSerializer
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserSerializer


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
