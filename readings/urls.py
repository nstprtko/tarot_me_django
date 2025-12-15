
from django.urls import path
from . import views
from .views.homepage import HomePageView
from .views.random_card import RandomCardView
from .views.expanded_reading import ExpandedReadingView
from .views.love_reading import LoveReadingView

app_name = "readings"

urlpatterns = [
    path("homepage", HomePageView.as_view(), name="homepage"),
    path("randomcard", RandomCardView.as_view(), name="randomcard"),
    path("lovereading", LoveReadingView.as_view(), name="lovereading"),
    path("expandedreading", ExpandedReadingView.as_view(), name="expandedreading"),
    path("api/draw/", views.api_draw, name="api_draw"),
    path("api/add_extra/", views.api_add_extra, name="api_add_extra"),
    path("api/card_of_day/", views.api_card_of_day, name="api_card_of_day"),
    path("policy/", views.policy_view, name="policy"),
]

