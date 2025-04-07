from django.utils import timezone # type:ignore
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from model_utils.choices import Choices
from model_utils.models import TimeStampedModel, UUIDModel
from .manager import UserManager
import re

# ==============================
# CHOICE DEFINITIONS
# ==============================

ROLE_CHOICES = Choices("artist", "artist_manager", "super_admin")
GENDER_CHOICES = Choices("male", "female", "other")
GENRE_CHOICES = Choices(
    "rnb",
    "country",
    "classic",
    "rock",
    "jazz",
    "pop",
    "indie_folk",
    "pop_rock",
    "alternative_rock",
    "soul",
)

# ==============================
# UTILITY FUNCTIONS
# ==============================


def validate_date(value):
    """Ensure date is not in the future."""
    if value and value > timezone.now().date():
        raise ValidationError(_("Date must not be in the future."))


def validate_phone(value):
    """Ensure phone number is valid."""
    if not re.match(r"^\+?1?\d{9,15}$", value):
        raise ValidationError(
            _(
                "Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
            )
        )


# ==============================
# USER MODEL
# ==============================


class User(AbstractBaseUser, PermissionsMixin, TimeStampedModel, UUIDModel):
    """Custom user model."""

    email = models.EmailField(_("Email Address"), max_length=255, unique=True)
    password = models.CharField(_("Password"), max_length=255)
    is_staff = models.BooleanField(_("Is Staff?"), default=False)
    is_active = models.BooleanField(_("Is Active?"), default=True)
    date_joined = models.DateTimeField(_("Joined Date"), auto_now_add=True)
    role = models.CharField(
        _("Role"), max_length=20, choices=ROLE_CHOICES, default=ROLE_CHOICES.artist
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = _("User ")

    def __str__(self) -> str:
        """String representation of the user."""
        return self.email

    def set_password(self, raw_password):
        """Set password using Django's hashing method."""
        self.password = make_password(raw_password)

    def get_absolute_url(self) -> str:
        """Get URL for user detail view."""
        return reverse("users:detail", kwargs={"pk": self.id})


# ==============================
# PROFILE MODELS
# ==============================


class Profile(UUIDModel, TimeStampedModel):
    """Abstract base profile model."""

    date_of_birth = models.DateField(
        _("Date of Birth"), null=True, blank=True, validators=[validate_date]
    )
    gender = models.CharField(
        _("Gender"), max_length=10, choices=GENDER_CHOICES, default=GENDER_CHOICES.male
    )
    address = models.CharField(_("Full Address"), max_length=255, null=True, blank=True)

    class Meta:
        abstract = True


class UserProfile(Profile):
    """User  profile model."""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    first_name = models.CharField(
        _("First Name"), max_length=255, null=True, blank=True
    )
    last_name = models.CharField(_("Last Name"), max_length=255, null=True, blank=True)
    phone = models.CharField(
        _("Phone Number"),
        max_length=15,
        null=True,
        blank=True,
        validators=[validate_phone],
    )

    class Meta:
        verbose_name = _("User  Profile")

    def __str__(self) -> str:
        """String representation of the profile."""
        return (
            f"{self.first_name} {self.last_name}".strip()
            if self.first_name
            else f"Profile of {self.user.email}"
        )


class ManagerProfile(Profile):
    """Manager profile model."""

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="manager_profile"
    )
    name = models.CharField(_("Name"), max_length=255)  # Required field
    company_name = models.CharField(
        _("Company Name"), max_length=255, null=True, blank=True
    )
    company_email = models.EmailField(_("Company Email"), null=True, blank=True)
    company_phone = models.CharField(
        _("Company Phone"),
        max_length=15,
        null=True,
        blank=True,
        validators=[validate_phone],
    )

    class Meta:
        verbose_name = _("Manager Profile")

    def __str__(self) -> str:
        """String representation of the manager."""
        return f"Manager: {self.name}"


class ArtistProfile(Profile):
    """Artist profile model."""

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="artist_profile"
    )
    manager = models.ForeignKey(
        ManagerProfile,
        on_delete=models.CASCADE,
        related_name="artists",
        null=True,
        blank=True,
    )
    name = models.CharField(_("Name"), max_length=255)  # Required field
    first_release_year = models.PositiveIntegerField(
        _("First Release Year"), null=True, blank=True
    )
    no_of_albums_released = models.PositiveIntegerField(
        _("Number of Albums Released"), default=0
    )

    class Meta:
        verbose_name = _("Artist Profile")

    def __str__(self) -> str:
        """String representation of the artist."""
        return f"Artist: {self.name}"


# ==============================
# MUSIC MODELS
# ==============================


class Music(UUIDModel, TimeStampedModel):
    """Music model definition."""

    title = models.CharField(_("Title"), max_length=255)  # Required field
    album_name = models.CharField(
        _("Album Name"), max_length=255, null=True, blank=True
    )
    release_date = models.DateTimeField(_("Release Date"), null=True, blank=True)
    genre = models.CharField(
        _("Genre"), max_length=20, choices=GENRE_CHOICES, default=GENRE_CHOICES.rnb
    )
    created_by = models.ForeignKey(
        ArtistProfile,
        on_delete=models.CASCADE,
        related_name="created_musics",
        null=True,
        blank=True,
    )
    artist = models.ForeignKey(
        ArtistProfile,
        on_delete=models.CASCADE,
        related_name="musics",
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = _("Music")

    def __str__(self) -> str:
        """String representation of the music."""
        return f"{self.title} ({self.album_name})" if self.album_name else self.title

    def get_absolute_url(self) -> str:
        """Get URL for music detail view."""
        return reverse("music:detail", kwargs={"pk": self.id})
