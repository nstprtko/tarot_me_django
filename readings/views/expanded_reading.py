from django.views.generic import TemplateView 
from .__init__ import ReadingService
from ..models import Card
from random import choice, sample
from django.shortcuts import render

class ExpandedReadingView(TemplateView):
    template_name= 'readings/reading.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pks = list(Card.objects.values_list('pk', flat=True))
        random_pks = sample(pks, 3)
        random_objs = list(Card.objects.filter(pk__in=random_pks))
        expanded_reading=ReadingService()
        meaning = expanded_reading.generate_reading_multuple(random_objs)
        context['cards'] = random_objs
        context['meaning'] = meaning
        return context
    def post(self, request, *args, **kwargs):
        loaded_names= request.POST.getlist('loaded_cards')
        existing_cards = list(Card.objects.filter(name__in=loaded_names))
        existing_cards.sort(key=lambda c: loaded_names.index(c.name))
        
        if len(existing_cards) >= 9:
            return render(request, self.template_name, {
                'cards': existing_cards,
                # Optional: Keep the old meaning or send a "Reading Complete" message
                'meaning': "Your reading is complete. Reflect on these 9 cards." 
            })
        
        new_cards = list(Card.objects.exclude(name__in=loaded_names).order_by('?')[:3])
        meaning = ReadingService().generate_reading_multuple(new_cards)
        
        return render(request, self.template_name,{
            'cards': existing_cards + new_cards,
            'meaning': meaning
        })
    
class ExpandedReadingService(ReadingService):
    INSTRUCTION="You are a mystical, whimsical tarot reader. Provide sensual reading about persons life and prospects. Explain the meaning of the cards and give guidence. Do not use asterisks"
