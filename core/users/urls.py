from django.urls import path
from .views import UserListView, UserCreateView, UserDetailView

app_name = "users"

urlpatterns = [
    path("users/", UserListView.as_view(), name="user-list"),  # List all users (GET)
    path("users/create/", UserCreateView.as_view(), name="user-create"),  # Create a new user (POST)
    path("users/<uuid:pk>/", UserDetailView.as_view(), name="user-detail"),  # Retrieve, update, delete a user (GET, PUT, DELETE)
]
