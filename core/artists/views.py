from rest_framework.views import APIView
from rest_framework import permissions, status
from rest_framework.response import Response
from core.serializers import ArtistProfileSerializer
from .services import (
    get_raw_artist_profile_list_queries,
    get_raw_artist_profile_detail_queries,
    create_raw_artist_profile_queries,
    update_raw_artist_profile_queries,
    delete_raw_artist_profile_queries,
)

class ArtistProfileCreateView(APIView):
    """View for creating Artist Profiles."""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ArtistProfileSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            success, data = create_raw_artist_profile_queries(
                request.user.id, serializer.validated_data
            )
            if success:
                return Response(data, status=status.HTTP_201_CREATED)
            return Response(
                {"error": "Failed to create artist profile."},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response({"error": "Invalid data provided.", "details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
class ArtistProfileListView(APIView):
    """View for listing Artist Profiles."""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ArtistProfileSerializer

    def get(self, request):
        success, data = get_raw_artist_profile_list_queries()
        if success:
            return Response(data, status=status.HTTP_200_OK)
        return Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ArtistProfileDetailView(APIView):
    """View for retrieving, updating, or deleting an Artist Profile."""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ArtistProfileSerializer

    def get(self, request, pk):
        success, data = get_raw_artist_profile_detail_queries(pk)
        if success:
            # Check if the user is the owner of the profile or a super admin
            if request.user.is_superuser or str(data["user_id"]) == str(
                request.user.id
            ):
                return Response(data, status=status.HTTP_200_OK)
            else:
                return Response(
                    {"error": "You do not have permission to view this profile."},
                    status=status.HTTP_403_FORBIDDEN,
                )
        return Response(data, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        # Check if the user is the owner of the profile or a super admin
        success, data = get_raw_artist_profile_detail_queries(pk)
        if not success:
            return Response(data, status=status.HTTP_404_NOT_FOUND)
        if not request.user.is_superuser and str(data["user_id"]) != str(
            request.user.id
        ):
            return Response(
                {"error": "You do not have permission to edit this profile."},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = self.serializer_class(data=request.data, partial=True)
        if serializer.is_valid():
            success, data = update_raw_artist_profile_queries(
                pk, serializer.validated_data
            )
            if success:
                return Response(data, status=status.HTTP_200_OK)
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        return Response(
            {"error": "Invalid data provided.", "details": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, pk):
        # Check if the user is the owner of the profile or a super admin
        success, data = get_raw_artist_profile_detail_queries(pk)
        if not success:
            return Response(data, status=status.HTTP_404_NOT_FOUND)
        if not request.user.is_superuser and str(data["user_id"]) != str(
            request.user.id
        ):
            return Response(
                {"error": "You do not have permission to delete this profile."},
                status=status.HTTP_403_FORBIDDEN,
            )
        success, data = delete_raw_artist_profile_queries(pk)
        if success:
            return Response(data, status=status.HTTP_204_NO_CONTENT)
        return Response(data, status=status.HTTP_404_NOT_FOUND)
