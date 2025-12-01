from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from .utils import generate_ai_reading, get_random_cards, deterministic_card_of_day
from .models import Reading
import random 
import json
import requests
from pathlib import Path
from django.views.generic import TemplateView 
from random import choice, sample
from .models import Card

class IndexView(TemplateView):
    template_name= 'readings/index.html'

class RandomCardView(TemplateView):
    template_name= 'readings/random_card.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pks = Card.objects.values_list('pk', flat=True)
        random_pk = choice(pks)
        random_obj = Card.objects.get(pk=random_pk)
        context['card'] = random_obj
        return context
    
    
        
    
    
class LoveReadingView(TemplateView):
    template_name= 'readings/love_reading.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pks = list(Card.objects.values_list('pk', flat=True))
        random_pks = sample(pks, 3)
        random_objs = Card.objects.filter(pk__in=random_pks)
        context['cards'] = random_objs
        return context
    
class ExpandedReadingView(TemplateView):
    template_name= 'readings/reading.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pks = list(Card.objects.values_list('pk', flat=True))
        random_pks = sample(pks, 3)
        random_objs = Card.objects.filter(pk__in=random_pks)
        context['cards'] = random_objs
        return context

@require_http_methods(["GET"])
def api_draw(request):
    """
    Draw the initial 3 cards and generate AI reading.
    Query param: ?type=love or ?type=general
    Returns JSON: {cards: [...], reading: "...", reading_id: N}
    """
    reading_type = request.GET.get("type", "general")
    cards = get_random_cards(3)
    ai_text = generate_ai_reading(cards, reading_type=reading_type)
    reading = Reading.objects.create(
        user=request.user if request.user.is_authenticated else None,
        reading_type=reading_type,
        cards=cards,
        ai_text=ai_text
    )
    return JsonResponse({"cards": cards, "reading": ai_text, "reading_id": reading.id})


@require_http_methods(["POST"])
@login_required  # require login to add extras so we can track daily quota
def api_add_extra(request):
    """
    Adds +3 cards to an existing reading. Expects JSON body {"reading_id": N}.
    Enforces per-user daily quota: non-premium users can add extras max 2 times/day.
    """
    try:
        payload = json.loads(request.body.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        return HttpResponseBadRequest("invalid JSON")

    reading_id = payload.get("reading_id")
    if not reading_id:
        return HttpResponseBadRequest("missing reading_id")

    reading = get_object_or_404(Reading, pk=reading_id)

    # only owner can modify their reading
    if reading.user and reading.user != request.user:
        return JsonResponse({"error": "not_owner"}, status=403)

    profile = request.user.profile
    profile.reset_if_needed()

    if not profile.is_premium and profile.daily_extra_uses >= 2:
        return JsonResponse({"error": "daily_limit_reached"}, status=403)

    existing_names = {c["name"] for c in reading.cards}
    new_cards = get_random_cards(3, exclude_names=existing_names)
    reading.cards.extend(new_cards)
    reading.extra_adds += 1
    reading.ai_text = generate_ai_reading(reading.cards, reading_type=reading.reading_type)
    reading.save()

    if not profile.is_premium:
        profile.daily_extra_uses += 1
        profile.save()

    return JsonResponse({"cards": reading.cards, "reading": reading.ai_text, "extra_adds": reading.extra_adds})


@require_http_methods(["GET"])
def api_card_of_day(request):
    """
    Return deterministic 'card of the day' for the user (or anon).
    No AI call — uses prewritten meanings.
    """
    cod = deterministic_card_of_day(request.user if request.user.is_authenticated else None)
    if not cod:
        return JsonResponse({"error": "no_cards_loaded"}, status=500)
    return JsonResponse({"card": cod})


