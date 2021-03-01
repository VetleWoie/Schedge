from django import forms

class NameForm(forms.Form):
    your_name = forms.CharField(label='Your name', max_length=100)
    your_dog = forms.CharField(label='Your dog', max_length=100)