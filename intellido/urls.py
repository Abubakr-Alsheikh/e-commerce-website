from django.urls import path, include 
from rest_framework.routers import DefaultRouter
from .views import TaskViewSet, SignupView # Import your viewsets
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

router = DefaultRouter()
router.register(r'tasks', TaskViewSet, basename='task') # Register TaskViewSet with the router

urlpatterns = [
    path('', include(router.urls)),  # InclFude URLs from the router
    path('api/signup/', SignupView.as_view(), name='signup'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]