from django.db import models
from django.conf import settings
from django.urls import reverse

class Movie(models.Model):
    page = models.IntegerField(default=0)
    movie_id = models.IntegerField(unique=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    original_language = models.CharField(max_length=10, blank=True, null=True)
    original_title = models.CharField(max_length=255, blank=True, null=True)
    overview = models.TextField(blank=True, null=True)
    poster_path = models.CharField(max_length=255, blank=True, null=True)
    backdrop_path = models.CharField(max_length=255, blank=True, null=True)
    media_type = models.CharField(max_length=20, blank=True, null=True)
    popularity = models.FloatField(default=0)
    release_date = models.DateField(blank=True, null=True)
    video = models.BooleanField(default=False)
    vote_average = models.FloatField(default=0)
    vote_count = models.IntegerField(default=0)
    
    def get_absolute_url(self):
        """Returns the absolute URL for the Movie detail view."""
        return reverse('screen-scene:movie_detail', args=[self.id])

    def __str__(self):
        return f"Page: {self.page} --- Title: {self.title}"
    
class Favorite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'movie') # Ensure a user can only favorite a movie once
