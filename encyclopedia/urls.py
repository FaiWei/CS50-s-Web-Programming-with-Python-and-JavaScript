from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("search", views.search, name="search"),
    path("wiki/<str:title>", views.wiki, name="wiki"),
    path("edit/<str:title>", views.edit, name="edit"),
    path("new", views.new, name="new"),
    path("random", views.random, name="random"),
    path("error", views.error, name="error") 
]
