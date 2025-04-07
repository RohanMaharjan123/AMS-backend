import jwt
from datetime import datetime, timedelta
from django.conf import settings
from .models import User


def generate_access_token(user: User):
    """Generate a JWT token for a given user."""
    payload = {
        "user_id": str(user.id),
        "email": user.email,
        "role": user.role,
        "exp": datetime.utcnow() + timedelta(seconds=settings.JWT_EXP_DELTA_SECONDS),
    }
    access = jwt.encode(
        payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )
    return access


def generate_refresh_token(user: User):
    """Generate a JWT token for a given user."""
    payload = {
        "user_id": str(user.id),
        "email": user.email,
        "role": user.role,
        "exp": datetime.utcnow() + timedelta(hours=settings.JWT_EXP_DELTA_HOURS),
    }
    refresh = jwt.encode(
        payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )
    return refresh


def decode_jwt_token(token):
    """Decode a JWT token and return the payload."""
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
