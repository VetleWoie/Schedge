from django.contrib import admin
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User


# from .models import User
# Register your models here.

# admin.site.register(User)

def createUser(request):
    #Add user to new user database
    username = request.POST['username']
    firstname = request.POST['firstname']
    lastname = request.POST['lastname']
    email = request.POST['email']
    password = request.POST['password1']

    u = User.objects.create_user(username, 
                                email=email, 
                                password=password,
                                first_name=firstname,
                                last_name=lastname)
