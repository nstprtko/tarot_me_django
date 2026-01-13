from django.views.generic import TemplateView 
from .__init__ import CardOfTheDayService as ReadingService
from ..models import Card
from random import choice, sample
from django.shortcuts import render


class LoveReadingService(ReadingService):
    INSTRUCTION="You are a mystical, whimsical tarot reader. Provide sensual reading about the person's love life according to the cards. be romantic. Do not use asterisks"


class LoveReadingView(TemplateView):
    template_name = 'readings/love_reading.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pks = list(Card.objects.values_list('pk', flat=True))
        random_pks = sample(pks, 3)
        random_objs = list(Card.objects.filter(pk__in=random_pks))
        love_reading = LoveReadingService()
        meaning = love_reading.generate_reading_multuple(random_objs)
        context['cards'] = random_objs
        context['meaning'] = meaning
        return context
    
    def post(self, request, *args, **kwargs):
        loaded_names = request.POST.getlist('loaded_cards')
        existing_cards = list(Card.objects.filter(name__in=loaded_names))
        existing_cards.sort(key=lambda c: loaded_names.index(c.name))
        
        if len(existing_cards) >= 9:
            return render(request, self.template_name, {
                'cards': existing_cards,
                'meaning': "Your love reading is complete. Reflect on these 9 cards and what they reveal about your romantic journey."
            })
        
        new_cards = list(Card.objects.exclude(name__in=loaded_names).order_by('?')[:3])
        meaning = LoveReadingService().generate_reading_multuple(new_cards)
        
        return render(request, self.template_name, {
            'cards': existing_cards + new_cards,
            'meaning': meaning
        })