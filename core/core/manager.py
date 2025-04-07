from typing import Optional

from django.contrib.auth.models import BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.utils.encoding import force_str


class UserManager(BaseUserManager):
    """Manager for custom user with email as username field."""

    def _create_user(self, email: str, password: Optional[str], **extra_fields):
        """
        Create and save a user with the given email and password.
        """
        if not email:
            raise ValueError(_("The given email must be set."))

        email = self.normalize_email(force_str(email))  # Ensures correct encoding
        user = self.model(email=email, **extra_fields)

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()  # Ensures the user cannot authenticate without setting a password

        user.save(using=self._db)
        return user

    def create_user(self, email: str, password: Optional[str] = None, **extra_fields):
        """Create, save, and return a new user."""
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        extra_fields.setdefault("is_active", True)  # Ensure users are active by default

        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email: str, password: str, **extra_fields):
        """Create, save, and return a new superuser."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields["is_staff"] is not True:
            raise ValueError(_("Superuser must have is_staff set to True."))
        if extra_fields["is_superuser"] is not True:
            raise ValueError(_("Superuser must have is_superuser set to True."))

        return self._create_user(email, password, **extra_fields)
