from rest_framework import serializers
def validate_password_match(attrs):
    """Validate that password and confirm_password match."""
    password = attrs.get("password")
    confirm_password = attrs.get("confirm_password")

    if password != confirm_password:
        raise serializers.ValidationError({"confirm_password": "Passwords must match."})

    return attrs


def validate_login_credentials(attrs):
    """Validate that username and password are provided."""
    email = attrs.get("email")
    password = attrs.get("password")

    if not email or not password:
        raise serializers.ValidationError({"detail": "Please provide both email and password."})

    return attrs