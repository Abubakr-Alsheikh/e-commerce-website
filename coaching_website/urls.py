from . import views
from django.urls import path

app_name = 'coach'
urlpatterns = [
    path('', views.index, name='index'),
    path('coaching-request/', views.coaching_request_view, name='coaching_request'),
]