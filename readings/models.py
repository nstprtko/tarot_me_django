
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Card(models.Model):
    """
    One DB row per tarot card.
    We store upright/reversed text, image filename, and a slug for URLs.
    """
    name = models.CharField(max_length=120, unique=True)
    upright = models.TextField()
    reversed = models.TextField()
    image = models.CharField(max_length=200)  # e.g. "the_fool.jpg"
    slug = models.SlugField(max_length=140, unique=True)

    def __str__(self):
        return self.name


class Profile(models.Model):
    """
    Per-user profile to track premium status and daily extra-add usage.
    daily_extra_uses = how many times user used +3 extras today (free limit: 2).
    last_reset = date when daily_extra_uses was last reset.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    is_premium = models.BooleanField(default=False)
    daily_extra_uses = models.IntegerField(default=0)
    last_reset = models.DateField(default=timezone.now)

    def reset_if_needed(self):
        """
        If the stored last_reset date is not today, reset the counter and update last_reset.
        Call this at the beginning of any request that needs to check/increment daily quota.
        """
        today = timezone.now().date()
        if self.last_reset != today:
            self.daily_extra_uses = 0
            self.last_reset = today
            self.save()

    def __str__(self):
        return f"Profile({self.user.username})"


class Reading(models.Model):
    """
    Stores a snapshot of a tarot reading:
    - user (nullable for anonymous)
    - reading_type: 'general' or 'love'
    - cards: JSONField to snapshot card state (name, reversed flag, image, texts)
    - ai_text: generated text from Ollama for this snapshot
    - extra_adds: how many times +3 extras were added to this reading
    - created_at: timestamp
    """
    READING_TYPES = [
        ("general", "General"),
        ("love", "Love"),
    ]

    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    reading_type = models.CharField(max_length=10, choices=READING_TYPES, default="general")
    cards = models.JSONField()
    ai_text = models.TextField(blank=True)
    extra_adds = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reading #{self.pk} ({self.reading_type}) - {self.created_at:%Y-%m-%d %H:%M}"
    
    """Card mirrors JSON deck in DB — easier to query, avoid file I/O at runtime, editable via admin.

Profile tracks whether a user is premium and how many extra-adds they used today. reset_if_needed() enforces daily reset.

Reading snapshots the cards and the AI text so readings remain immutable for history/logging."""
