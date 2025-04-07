from django.contrib import admin
from .models import UserProfile, ArtistProfile, Music, ManagerProfile


class MusicAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "album_name",
        "release_date",
        "genre",
        "created_by",
        "artist",
    )


admin.site.register(UserProfile)
admin.site.register(ArtistProfile)
admin.site.register(ManagerProfile)

admin.site.register(Music, MusicAdmin)
