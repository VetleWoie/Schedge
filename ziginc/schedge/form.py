from django import forms
from django.contrib.auth.models import User


class NameForm(forms.Form):
    username = forms.CharField(label='Username', max_length=100)
    firstname = forms.CharField(label='First name', max_length=100)
    lastname = forms.CharField(label='Last name', max_length=100)
    email = forms.EmailField(label='Email', max_length=20)
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Rewrite password', widget=forms.PasswordInput)
    
    def clean_password(self):
        #Check that passwords match
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password1 != password2:
            raise forms.ValidationError("Passwords don't match.")

        return self.cleaned_data

    def clean_username(self):
        #Check that username hasn't been used before
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username allready taken.")

    def clean_email(self):
        #Check that email is unique
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email is already in use.")

