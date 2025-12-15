from django.views.generic import TemplateView 
from .__init__ import ReadingService
from ..models import Card
from random import choice, sample

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
    
class ExpandedReadingService(ReadingService):
    INSTRUCTION="You are a mystical, whimsical tarot reader. Provide sensual reading about persons life and prospects. Use only 3 sentences"
