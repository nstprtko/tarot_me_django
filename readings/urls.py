
from django.urls import path
from . import views

app_name = "readings"

urlpatterns = [
    path("", views.index_view, name="index"),
    path("api/draw/", views.api_draw, name="api_draw"),
    path("api/add_extra/", views.api_add_extra, name="api_add_extra"),
    path("api/card_of_day/", views.api_card_of_day, name="api_card_of_day"),
]

