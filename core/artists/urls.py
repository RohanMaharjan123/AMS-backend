from django.urls import path
from .views import (
    ArtistProfileCreateView,
    ArtistProfileListView,
    ArtistProfileDetailView,
)

app_name = "artists"

urlpatterns = [
    path(
        "artists/", ArtistProfileListView.as_view(), name="artist-list"
    ),  # List all artists (GET)
    path(
        "artists/create/", ArtistProfileCreateView.as_view(), name="artist-create"
    ),  # Create artist profile (POST)
    path(
        "artists/<uuid:pk>/", ArtistProfileDetailView.as_view(), name="artist-detail"
    ),  # Retrieve, update, delete
]
