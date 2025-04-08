from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import JSONParser  # type: ignore # Import JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication
from django.contrib.auth import logout


from users.services import (
    get_raw_login_queries,
    get_raw_register_queries,
)  # Import connection

from .serializers import LoginSerializer, RegisterSerializer
from .utils import generate_access_token, generate_refresh_token
from core.models import UserProfile


class LoginView(APIView):
    """User Login View."""

    permission_classes = [permissions.AllowAny]
    serializer_class = LoginSerializer
    parser_classes = [JSONParser]  # Add JSONParser

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            password = serializer.validated_data["password"]

            # Use get_raw_login_queries to get the user
            user = get_raw_login_queries(email, password)

            if user is not None:
                request.user = user
                access = generate_access_token(user)
                refresh = generate_refresh_token(user)
                # Get the user's profile to retrieve the name
                try:
                    user_profile = UserProfile.objects.get(user=user)
                    user_name = f"{user_profile.first_name} {user_profile.last_name}".strip()
                except UserProfile.DoesNotExist:
                    user_name = user.email  # Fallback to email if profile not found

                return Response(
                    {
                        "access": access,
                        "refresh": refresh,
                        "user_id": str(user.id),
                        "email": user.email,
                        "role": user.role,
                        "name": user_name,  # Include the user's name
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"error": "Invalid credentials"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegisterView(APIView):
    """User Registration View."""

    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer
    parser_classes = [JSONParser]  # Add JSONParser

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            first_name = serializer.validated_data["first_name"]
            last_name = serializer.validated_data["last_name"]
            email = serializer.validated_data["email"]
            password = serializer.validated_data["password"]
            phone = serializer.validated_data["phone"]
            dob = serializer.validated_data["dob"]
            gender = serializer.validated_data["gender"]
            address = serializer.validated_data["address"]
            role = serializer.validated_data["role"]

            success, errors = get_raw_register_queries(
                first_name,
                last_name,
                email,
                password,
                phone,
                dob,
                gender,
                address,
                role,
            )

            if success:
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(errors, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# logout functionality here
class LogoutView(APIView):
    """
    Logout view to handle user logout.
    """

    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication]

    def post(self, request):
        """
        Logs out the current user.
        """
        logout(request)
        return Response(
            {"message": "Successfully logged out."}, status=status.HTTP_200_OK
        )