# readings/utils.py
import requests
from django.conf import settings
from .models import Card
import random
import hashlib
import datetime

# configurable defaults via settings.py
OLLAMA_URL = getattr(settings, "OLLAMA_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = getattr(settings, "OLLAMA_MODEL", "llama3")
OLLAMA_TIMEOUT = getattr(settings, "OLLAMA_TIMEOUT", 60)


def generate_ai_reading(cards, reading_type="general"):
    """
    Call local Ollama API to generate an interpretation.
    `cards` is a list of dicts with at least 'name' and 'reversed'.
    reading_type == 'love' -> add romantic instruction to prompt.
    Returns text or an error string.
    """
    summary = ", ".join([f"{c['name']} ({'reversed' if c.get('reversed') else 'upright'})" for c in cards])
    prompt = f"You are a mystical tarot reader. Interpret the cards as past, present, future: {summary}."
    if reading_type == "love":
        prompt = "Write the following reading in a romantic, empathetic tone. " + prompt

    payload = {"model": OLLAMA_MODEL, "prompt": prompt, "stream": False}
    try:
        r = requests.post(OLLAMA_URL, json=payload, timeout=OLLAMA_TIMEOUT)
        if r.status_code == 200:
            return r.json().get("response", "").strip()
        return f"Ollama error: {r.status_code}"
    except Exception as e:
        # return a safe error string for frontend display
        return f"Ollama unreachable: {e}"


def get_random_cards(n=3, exclude_names=None):
    """
    Return n card snapshots (dicts) chosen randomly from Card DB.
    Each snapshot contains name, reversed flag, image, upright text, reversed text.
    exclude_names: set of names to avoid duplicates with existing reading.
    """
    if exclude_names is None:
        exclude_names = set()
    else:
        exclude_names = set(exclude_names)

    all_cards = list(Card.objects.exclude(name__in=exclude_names))
    # if not enough distinct remaining, allow duplicates by sampling from full set
    if len(all_cards) < n:
        pool = list(Card.objects.all())
        choices = random.choices(pool, k=n)
    else:
        choices = random.sample(all_cards, k=n)

    snapshots = []
    for c in choices:
        rev_flag = random.choice([True, False])
        snapshots.append({
            "name": c.name,
            "reversed": rev_flag,
            "image": c.image,
            "upright": c.upright,
            "reversed_text": c.reversed,
        })
    return snapshots


def deterministic_card_of_day(user=None):
    """
    Deterministic 'card of the day' per user (or global for anonymous).
    Uses SHA256(date + user.id/anon) to choose an index. Returns card name, image, meaning.
    We return the prepared (upright) meaning and don't call AI for this feature.
    """
    cards = list(Card.objects.all())
    if not cards:
        return None
    seed = (str(user.id) if user else "anon") + datetime.date.today().isoformat()
    digest = hashlib.sha256(seed.encode()).hexdigest()
    idx = int(digest, 16) % len(cards)
    c = cards[idx]
    return {
        "name": c.name,
        "image": c.image,
        "meaning": c.upright  # pre-prepared text
    }
"""generate_ai_reading: single place for Ollama calls; adds romantic instruction when reading_type='love'.

get_random_cards: returns snapshot dicts (not DB objects) — perfect for storing to Reading.cards JSONField.

deterministic_card_of_day: stable per user/date; no AI required."""