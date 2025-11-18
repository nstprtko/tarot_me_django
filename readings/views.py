from django.shortcuts import render
from django.http import JsonResponse
import random 
import json
import requests
from pathlib import Path

# base_dir points to where root

BASE_DIR = Path(__file__).resolve().parent.parent
with open(BASE_DIR/"data"/"tarot_cards.json", "r", encoding='utf-8') as f:
    tarot_cards = json.load(f)
    
def index_view(request):
    return render(request, 'readings/index.html')


def draw_three_cards():
    cards = random.sample(tarot_cards, 3)
    for c in cards:
        c["reversed"] = random.choice([True, False])
    return cards

def generate_ai_reading(cards):
    summary = ", ".join(
        [f"{c['name']} ({'reversed' if c['reversed'] else 'upright'})" for c in cards]
    )
    prompt = f"""
    You are a mystical tarot reader.
    Provide a poetic, insightful interpretation for these three tarot cards:
    {summary}.
    Explain them as past, present, and future in one short paragraph.
    """
    try:
        resp = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "llama3", "prompt": prompt, "stream": False},
            timeout=60
        )
        if resp.status_code == 200:
            return resp.json().get("response", "").strip()
        return f"Ollama error {resp.status_code}"
    except Exception as e:
        return f"Ollama not reachable: {e}"
    
def index(request):
    return render(request, 'index.html')

def api_draw(request):
    cards = draw_three_cards()
    ai_reading = generate_ai_reading(cards)
    return JsonResponse({'cards': cards, 'reading': ai_reading})
