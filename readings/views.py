from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .utils import generate_ai_reading, get_random_cards, deterministic_card_of_day
from .models import Reading
import random 
import json
import requests
from pathlib import Path
from django.views.generic import TemplateView 
from random import choice, sample
from .models import Card
import os
from openai import OpenAI 


    
    
# card of the day explanation, expanded readings, love readings explanation   
class ReadingService:
    HOST = getattr(settings, "OLLAMA_HOST", "http://localhost:11434")
    MODEL = getattr(settings, "OLLAMA_MODEL", "llama3")
    INSTRUCTION = "You are a mystical tarot reader. Interpret the cards as past, present, future"
       
    def __init__(self):
        self.client = OpenAI(
        base_url=f"{self.HOST}/v1",
        api_key="ollama",
        )
        
    def format_message(self, card_name, card_meaning):
        return f"""Card of the day: {card_name},
                Meaning : {card_meaning}
                Provide a whimsical, inspiring interpretation for today's guidance. Maximum 3 sentences"""
                
                
    def generate_interpretation(self, card_name, card_meaning):
        #call the previously creeated func to know the card and meaning(should we make it more efficient? put it into one?
        # also gives instruction to analyse todays message)
        message=self.format_message(card_name, card_meaning)
        # call self.client to access ai funcs(?) 
        response = self.client.chat.completions.create(
            model=self.MODEL,
            messages=[
                {"role": "system", "content":self.INSTRUCTION},
                {"role": "user", "content": message}
                ]
        )
        # yeah so basically about what is this part of the code above...
        # uhm i understand it and at the same time i dont 
        #for model we use the ollama model stated earlier 
        # why do we call it messages idk but role system we assign a way to behave
        # and by role user we give an actual prompt of what to do
        #makes sense right T T
        return response.choices[0].message.content.strip()
        # choices[0] returns the first response
        # message.content - the actual message 
        # strip ;) is actully not nessesary 
        
        
        
        
        
       
       
       #def get_message(data):
           #return    self.MESSAGE.format(data)
       # what is the point of this function...
       #def ask_for_readings(data: dict):
        # ???? переставити на початок коду в імпорти
           #import os
           #from openai import OpenAI

           #client = OpenAI(
               #This is the default and can be comitted
               #base_url = 'http://localhost:11434/v1',
               #api_key = 'ollama',
           #)

           #response = client.responses.create(
               #model="llama2",
               #instruction = self.INSTRUCTION,
               #input=self.get_message(data),
           #)

           #print(response.output_text)
           

class CardOfTheDayService(ReadingService):
    INSTRUCTION="You are a mystical, whimsical tarot reader. Provide brief, inspiring daily guidance."

class ExpandedReadings(ReadingService):
    pass

class LoveReadingService(ReadingService):
    pass


class IndexView(TemplateView):
    template_name= 'readings/index.html'

class RandomCardView(TemplateView):
    template_name = 'readings/random_card.html'
    
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
    Add ?ai=true to get AI interpretation.
    """
    # Get the card (from utils.py)
    cod = deterministic_card_of_day(request.user if request.user.is_authenticated else None)
    
    if not cod:
        return JsonResponse({"error": "no_cards_loaded"}, status=500)
    
    # Generate AI interpretation if requested
    if request.GET.get("ai") == "true":
        service = CardOfTheDayService()  # ← Call the class here
        ai_interpretation = service.generate_interpretation(cod["name"], cod["meaning"])
        cod["ai_interpretation"] = ai_interpretation
    
    return JsonResponse({"card": cod})

