from django.views.generic import TemplateView 
from .__init__ import ReadingService
from ..models import Card
from random import choice, sample

# is this class useless?
class CardOfTheDayView(TemplateView):
    template_name= 'readings/random_card.html'
    
class CardOfTheDayService(ReadingService):
    INSTRUCTION="You are a mystical, whimsical tarot reader. Provide brief, inspiring daily guidance."
    
class RandomCardView(TemplateView):
    template_name = 'readings/random_card.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pks = Card.objects.values_list('pk', flat=True)
        random_pk = choice(pks)
        random_obj = Card.objects.get(pk=random_pk)
        card_of_the_day=CardOfTheDayService()
        meaning = card_of_the_day.generate_interpretation(random_obj.name, random_obj.upright)
        context['card'] = random_obj
        context['meaning'] = meaning
        return context