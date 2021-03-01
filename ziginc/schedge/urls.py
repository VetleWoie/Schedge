from django.urls import path, include
from django.views.generic.base import TemplateView
from . import views

from .views import signUpView

urlpatterns = [
    path('signup/', signUpView, name='signup'),    
    path('', include('django.contrib.auth.urls')),
]