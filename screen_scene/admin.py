from django.contrib import admin
from .models import Favorite, Movie

# Register your models here.
admin.site.register(Movie)
admin.site.register(Favorite)

