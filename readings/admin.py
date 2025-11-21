from django.contrib import admin
from .models import Card, Profile, Reading

# Register your models here.
@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "is_premium", "daily_extra_uses", "last_reset")
    readonly_fields = ("last_reset",)

@admin.register(Reading)
class ReadingAdmin(admin.ModelAdmin):
    list_display = ("id", "reading_type", "user", "created_at", "extra_adds")
    readonly_fields = ("cards", "ai_text", "created_at")