from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("signUp", views.signUp, name="signUp"),
    path("signIn", views.signIn, name="signIn"),
    path("createEvent", views.createEvent, name="createEvent"),
]