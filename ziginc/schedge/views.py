from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.template import loader
# from .models import User
# Create your views here.
# def home(request):
#     # users = User.objects.order_by("username")
#     template = loader.get_template("home.html")
#     context = {
#         "userList" : ""
#     }
#     return HttpResponse(template.render(context, request))
    # raise Http404("THIS DOES NOT Existss") #tis' was but a test
def signUp(request):
    return HttpResponse("signup page")
def signIn(request):
    template = loader.get_template("registration/login.html")
    context = {
        "":"" 
    }
    return HttpResponse(template.render(context, request))
def createEvent(request):
    raise Http404("THIS DOES NOT Existss") #tis' was but a test
