from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views # new

app_name = 'screen-scene'
urlpatterns = [
    path('', views.index, name='index'),
    path('movie/<int:movie_id>/', views.movie_detail, name='movie_detail'),
    path('load-more-movies/', views.load_more_movies, name='load_more_movies'),
    path('profile/', views.signup, name='profile'),
    path('favorites/', views.favorites, name='favorites'),
    path('movies/', views.movies, name='movies'), 
    path('movies/<int:movie_id>/toggle_favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('load_more_all_movies/', views.load_more_all_movies, name='load_more_all_movies'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.user_login, name='user_login'),
    path('logout/', views.user_logout, name='user_logout'),
    path('search/', views.search_movies, name='search_movies'), 
    path('load-more-search-results/', views.load_more_search_results, name='load_more_search_results'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)