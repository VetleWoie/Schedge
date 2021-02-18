from django.urls import path, include
from django.views.generic.base import TemplateView
from . import views

from .views import SignUpView
urlpatterns = [
    path('signup/' ,SignUpView,name='signup'),    
    path("createEvent", views.createEvent, name="createEvent"),
    path('', include('django.contrib.auth.urls')),
]