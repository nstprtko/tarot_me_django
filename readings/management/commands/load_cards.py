
import json
from django.core.management.base import BaseCommand
from pathlib import Path
from readings.models import Card

class Command(BaseCommand):
    help = "Load tarot_cards.json (in project root /data/) into Card model."

    def handle(self, *args, **options):
        base = Path.cwd()  # manage.py working dir (project root)
        data_file = base / "data" / "tarot_cards.json"
        if not data_file.exists():
            self.stdout.write(self.style.ERROR("data/tarot_cards.json not found in project root."))
            return

        with open(data_file, "r", encoding="utf-8") as f:
            cards = json.load(f)

        for c in cards:
            slug = c.get("name", "").lower().replace(" ", "-")
            Card.objects.update_or_create(
                name=c.get("name", ""),
                defaults={
                    "upright": c.get("upright", "") or c.get("meaning", ""),
                    "reversed": c.get("reversed", ""),
                    "image": c.get("image", ""),
                    "slug": slug,
                }
            )

        self.stdout.write(self.style.SUCCESS(f"Loaded {len(cards)} cards."))
"""Run python manage.py load_cards after migrations to populate cards table.

Works idempotently due to update_or_create."""