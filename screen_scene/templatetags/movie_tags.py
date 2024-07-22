from django import template

register = template.Library()

@register.filter
def get_rating_stars(vote_average):
    """Returns a list of True/False values for filled and empty stars based on vote average."""
    if vote_average is None: 
        return []  # Return an empty list for unrated movies
    stars = []
    for i in range(5):
        if i < round(vote_average / 2):
            stars.append(True)  # Filled star
        else:
            stars.append(False) # Empty star
    return stars
