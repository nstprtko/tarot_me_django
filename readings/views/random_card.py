from django.views.generic import TemplateView
# We import the base service from __init__ and rename it to 'ReadingService'
# so we can extend it below without naming conflicts.
from .__init__ import CardOfTheDayService as ReadingService
from ..models import Card
import random

class CardOfTheDayService(ReadingService):
    # This subclass overrides the instruction specifically for this view
    INSTRUCTION = "You are a mystical, whimsical tarot reader. Provide a brief explanation for this card for the day. Do not use asterisks"
    
class RandomCardView(TemplateView):
    template_name = 'readings/random_card.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Optimized way to get a random card (faster than fetching all PKs)
        random_obj = Card.objects.order_by('?').first()
        
        if random_obj:
            # Initialize the local service defined above
            service = CardOfTheDayService()
            meaning = service.generate_interpretation(random_obj.name, random_obj.upright)
            
            context['card'] = random_obj
            context['meaning'] = meaning
        else:
            context['error'] = "No cards found in the database."
            
        return context