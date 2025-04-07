from django.contrib.auth import get_user_model
from rest_framework import authentication, exceptions

from .utils import decode_jwt_token


class JWTAuthentication(authentication.BaseAuthentication):
    """Custom authentication class for JWT."""

    def authenticate(self, request):
        """Authenticate the request and return a two-tuple of (user, token)."""
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return None

        scheme, token = auth_header.split()
        if scheme.lower() != "bearer":
            return None

        payload = decode_jwt_token(token)
        if not payload:
            raise exceptions.AuthenticationFailed("Invalid token")

        user_id = payload.get("user_id")
        User = get_user_model()
        try:
            user = User.objects.get(id=user_id)
            # Set the role to the user object
            user.role = payload.get("role")
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed("No such user")

        return (user, token)
