from functools import reduce
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from urllib.parse import quote  # Use quote from urllib.parse
from django.template.loader import render_to_string
from django.contrib import messages
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from .models import Favorite, Movie
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
import re
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import requests
from django.urls import reverse  # Import reverse
from django.db.models import Q  # Import Q for complex queries


def index(request):
    page = request.GET.get("page", 1)  # Get page from query parameters, default to 1

    if page == "2":
        update_movie_data(request)

    latest_movies = Movie.objects.filter(
        release_date__gte=timezone.now() - timedelta(days=30)
    ).order_by("-release_date")[:16]

    # Get popular movies (using a higher threshold for popularity)
    popular_movies = Movie.objects.filter(popularity__gte=500)[:8]

    if request.user.is_authenticated:
        # Get the IDs of the user's favorite movies
        favorite_movie_ids = Favorite.objects.filter(user=request.user).values_list(
            "movie_id", flat=True
        )

        # Add a 'is_favorite' field to each movie in 'latest_movies' and 'popular_movies'
        for movie in latest_movies:
            movie.is_favorite = movie.id in favorite_movie_ids

        for movie in popular_movies:
            movie.is_favorite = movie.id in favorite_movie_ids

    context = {
        "latest_movies": latest_movies,
        "popular_movies": popular_movies,
        "featured_movie": popular_movies[:3],
        "IMG_PATH": "https://image.tmdb.org/t/p/w500",
        "current_page": page,  # Pass the current page to the template
    }

    return render(request, "screen_scene/index.html", context)


@require_POST  # Restrict this view to POST requests
def load_more_movies(request):
    start_from = int(request.POST.get("start_from", 0))
    movies_to_load = 8

    popular_movies = Movie.objects.filter(popularity__gte=500)[
        start_from : start_from + movies_to_load
    ]

    if request.user.is_authenticated:
        favorite_movie_ids = Favorite.objects.filter(user=request.user).values_list(
            "movie_id", flat=True
        )
        for movie in popular_movies:
            movie.is_favorite = movie.id in favorite_movie_ids

    rendered_movies = ""  # Start with an empty string

    for movie in popular_movies:  # Iterate through the movies
        rendered_movies += render_to_string(
            "screen_scene/components/movie_card.html",
            {"movie": movie, "IMG_PATH": "https://image.tmdb.org/t/p/w500"},
            request=request,
        )

    return JsonResponse({"html": rendered_movies})

def update_movie_data(request):
    for page in range(1, 6):
        api_url = f"https://api.themoviedb.org/3/discover/movie?sort_by=popularity.desc&api_key={settings.THEMOVIEDB_API_KEY}&page={page}"
        response = requests.get(api_url)

        if response.status_code == 200:
            data = response.json()
            movies = data["results"]

            for movie_data in movies:
                # **Update or create movie records:**
                movie, created = Movie.objects.update_or_create(
                    movie_id=movie_data["id"],  # Use movie_id as the lookup key
                    defaults={
                        "page": page,
                        "title": movie_data["title"],
                        "original_language": movie_data["original_language"],
                        "original_title": movie_data["original_title"],
                        "overview": movie_data["overview"],
                        "poster_path": movie_data["poster_path"],
                        "backdrop_path": movie_data["backdrop_path"],
                        "media_type": "movie",
                        "popularity": movie_data["popularity"],
                        "release_date": (
                            movie_data["release_date"]
                            if movie_data["release_date"]
                            else None
                        ),
                        "video": movie_data["video"],
                        "vote_average": movie_data["vote_average"],
                        "vote_count": movie_data["vote_count"],
                    },
                )
        else:
            return render(
                request, "screen_scene/index.html", {"error": "Error fetching data"}
            )


def movie_detail(request, movie_id):
    movie = get_object_or_404(Movie, pk=movie_id)

    is_favorite = False
    if request.user.is_authenticated:
        is_favorite = Favorite.objects.filter(user=request.user, movie=movie).exists()

    context = {
        "movie": movie,
        "IMG_PATH": "https://image.tmdb.org/t/p/w500",
        "is_favorite": is_favorite,
    }
    return render(request, "screen_scene/movie_detail.html", context)


def toggle_favorite(request, movie_id):
    if request.user.is_authenticated:
        movie = get_object_or_404(Movie, pk=movie_id)
        favorite, created = Favorite.objects.get_or_create(
            user=request.user, movie=movie
        )

        if not created:  # If the favorite already existed, delete it
            favorite.delete()
            is_favorite = False
        else:
            is_favorite = True

        return JsonResponse({"is_favorite": is_favorite})
    else:
        return JsonResponse(
            {"not_logged_in": True, "error": True}, status=401
        )  # 401 Unauthorized


@login_required
def favorites(request):
    favorite_movies = Favorite.objects.filter(user=request.user).values_list(
        "movie", flat=True
    )
    movies = Movie.objects.filter(id__in=favorite_movies)
    for movie in movies:
        movie.is_favorite = movie.id in favorite_movies

    # Pagination (optional but recommended)
    paginator = Paginator(movies, 4)  # Show 12 movies per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {"movies": page_obj, "IMG_PATH": "https://image.tmdb.org/t/p/w500"}
    return render(request, "screen_scene/favorites.html", context)


def movies(request):
    page = request.GET.get("page", 1)
    movies_to_load = 8

    all_movies = Movie.objects.all().order_by("-popularity", "-release_date")

    # Pagination
    paginator = Paginator(all_movies, movies_to_load)
    page_obj = paginator.get_page(page)

    if request.user.is_authenticated:
        favorite_movie_ids = Favorite.objects.filter(user=request.user).values_list(
            "movie_id", flat=True
        )
        for movie in page_obj:
            movie.is_favorite = movie.id in favorite_movie_ids

    context = {
        "movies": page_obj,
        "IMG_PATH": "https://image.tmdb.org/t/p/w500",
    }
    return render(request, "screen_scene/movies.html", context)


@require_POST
def load_more_all_movies(request):
    start_from = int(request.POST.get("start_from", 0))
    movies_to_load = 8

    movies = Movie.objects.all().order_by("-popularity", "-release_date")[
        start_from : start_from + movies_to_load
    ]

    if request.user.is_authenticated:
        favorite_movie_ids = Favorite.objects.filter(user=request.user).values_list(
            "movie_id", flat=True
        )
        for movie in movies:
            movie.is_favorite = movie.id in favorite_movie_ids

    rendered_movies = ""  # Start with an empty string

    for movie in movies:  # Iterate through the movies
        rendered_movies += render_to_string(
            "screen_scene/components/movie_card.html",
            {"movie": movie, "IMG_PATH": "https://image.tmdb.org/t/p/w500"},
            request=request,
        )

    return JsonResponse({"html": rendered_movies})


def search_movies(request):
    search_query = request.GET.get("q", "")

    if search_query:
        # 1.  Split the search query into words (allow for spaces and hyphens)
        search_terms = re.split(r"[- ]+", search_query)

        # 2.  Search in the database first, allowing partial matches for each word
        db_movies = Movie.objects.filter(
            reduce(lambda x, y: x | Q(title__icontains=y), search_terms, Q())
        ).order_by("-popularity", "-release_date")[:8]
        # 2. Fetch from TMDB if fewer than 8 results from the database
        if db_movies.count() < 8:
            api_url = f"https://api.themoviedb.org/3/search/movie?api_key={settings.THEMOVIEDB_API_KEY}&query={quote(search_query)}"
            response = requests.get(api_url)

            if response.status_code == 200:
                data = response.json()
                results = data["results"]

                # 3. Save/Update results from TMDB to the database
                for movie_data in results:
                    movie, created = Movie.objects.update_or_create(
                        movie_id=movie_data["id"],  # Use movie_id as the lookup key
                        defaults={
                            "page": 0,
                            "title": movie_data["title"],
                            "original_language": movie_data["original_language"],
                            "original_title": movie_data["original_title"],
                            "overview": movie_data["overview"],
                            "poster_path": movie_data["poster_path"],
                            "backdrop_path": movie_data["backdrop_path"],
                            "media_type": "search",
                            "popularity": movie_data["popularity"],
                            "release_date": (
                                movie_data["release_date"]
                                if movie_data["release_date"]
                                else None
                            ),
                            "video": movie_data["video"],
                            "vote_average": movie_data["vote_average"],
                            "vote_count": movie_data["vote_count"],
                        },
                    )

                # 4. Combine and sort results (database + API)
                all_movies = [
                    movie
                    for movie in Movie.objects.filter(
                        movie_id__in=[m["id"] for m in results]
                    )
                ]
                all_movies.sort(
                    key=lambda x: (
                        x.popularity,
                        (
                            x.release_date
                            if x.release_date
                            else timezone.now() - timedelta(days=365 * 100)
                        ),
                    ),
                    reverse=True,
                )  # Sort by popularity and then release date

            else:
                # Handle API error
                # ... (display an error message to the user)
                all_movies = db_movies  # Use only database results if API error
        else:
            all_movies = db_movies  # If there are 8 results from the database

        if request.user.is_authenticated:
            favorite_movie_ids = Favorite.objects.filter(user=request.user).values_list(
                "movie_id", flat=True
            )
            for movie in all_movies:
                movie.is_favorite = movie.id in favorite_movie_ids

        context = {
            "search_query": search_query,
            "movies": all_movies,  # Use the combined and sorted results
            "IMG_PATH": "https://image.tmdb.org/t/p/w500",
        }
        return render(request, "screen_scene/search_results.html", context)
    else:
        # Handle empty search query (optional)
        # ... (redirect back to the home page or display a message)
        pass


@require_POST
def load_more_search_results(request):
    search_query = request.POST.get("q", "")
    start_from = int(request.POST.get("start_from", 0))
    movies_to_load = 8

    if search_query:
        movies = Movie.objects.filter(Q(title__icontains=search_query)).order_by(
            "-popularity", "-release_date"
        )[start_from : start_from + movies_to_load]

        if request.user.is_authenticated:
            favorite_movie_ids = Favorite.objects.filter(user=request.user).values_list(
                "movie_id", flat=True
            )
            for movie in movies:
                movie.is_favorite = movie.id in favorite_movie_ids

        rendered_movies = ""  # Start with an empty string
        for movie in movies:  # Iterate through the movies
            rendered_movies += render_to_string(
                "screen_scene/components/movie_card.html",
                {"movie": movie, "IMG_PATH": "https://image.tmdb.org/t/p/w500"},
                request=request,
            )

        return JsonResponse({"html": rendered_movies})
    else:
        return JsonResponse({"error": "Missing search query"})


User = get_user_model()  # Get the User model


def signup(request):
    if request.user.is_authenticated:
        # User is already logged in, redirect to the home page or another page
        messages.info(request, "You are already logged in.")
        return redirect("screen-scene:index")  # Redirect to your home page

    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # **Specify the authentication backend:**
            login(request, user, backend="django.contrib.auth.backends.ModelBackend")
            messages.success(request, "Account created successfully!")
            return redirect("screen-scene:index")  # Redirect to your home page
    else:
        form = CustomUserCreationForm()
    return render(request, "screen_scene/signup.html", {"form": form})


def user_login(request):
    if request.user.is_authenticated:
        # User is already logged in, redirect to the home page or another page
        messages.info(request, "You are already logged in.")
        return redirect("screen-scene:index")  # Redirect to your home page

    if request.method == "POST":
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(request, username=username, password=password)
            if user is not None:
                # **Specify the authentication backend:**
                login(
                    request, user, backend="django.contrib.auth.backends.ModelBackend"
                )
                messages.info(request, f"You are now logged in as {username}.")
                return redirect("screen-scene:index")  # Redirect to your home page
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = CustomAuthenticationForm()
    return render(request, "screen_scene/login.html", context={"form": form})


@login_required
def user_logout(request):
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect("screen-scene:index")
