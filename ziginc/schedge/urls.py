from django.urls import path
from django.views.generic.base import TemplateView
from . import views

urlpatterns = [
    # path("", TemplateView.as_view(template_name='home.html'), name="home"),
    path("signUp", views.signUp, name="signUp"),
    path("signIn", views.signIn, name="signIn"),
    path("createEvent", views.createEvent, name="createEvent"),
]