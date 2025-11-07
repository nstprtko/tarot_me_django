from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('api/draw/', views.api_draw, name='api_draw'),
]
