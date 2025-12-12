from django.views.generic import TemplateView 

class HomePageView(TemplateView):
    template_name= 'readings/home_page.html'