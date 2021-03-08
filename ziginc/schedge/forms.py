from django import forms
from itertools import product
import datetime as dt
from django.forms.widgets import TextInput
from django.utils.dateparse import parse_duration

from django.forms.widgets import MultiWidget
from .models import Event, TimeSlot
from django.contrib.auth.models import User


class DateInput(forms.DateInput):
    input_type = "date"


class TimeInput(forms.DateInput):
    input_type = "time"


def max_date(years=10):
    """Returns the date in 10 years
    If leap day (29-02), return (28-02)"""
    today = dt.datetime.today()
    maxyear = today.year + years
    maxmonth = today.month

    # 28 on Feb 29 (leap day). 10 years after leap day is not leap year
    maxday = today.day if today.day != 29 or today.month != 2 else 28
    return dt.datetime(maxyear, maxmonth, maxday).strftime("%Y-%m-%d")


class EventForm(forms.ModelForm):
    # hours = forms.IntegerField(min_value=0)
    # minutes = forms.IntegerField(min_value=0)

    class Meta:
        model = Event
        fields = [
            "title",
            "startdate",
            "enddate",
            "description",
            "duration",
            "starttime",
            "endtime",
            "location",
            "image",
        ]

        today = dt.datetime.today().strftime("%Y-%m-%d")

        widgets = {
            "startdate": DateInput(attrs={"min": today, "max": max_date()}),
            "enddate": DateInput(attrs={"min": today, "max": max_date()}),
            "starttime": TimeInput(format=("HH:mm")),
            "endtime": TimeInput(format=("HH:mm")),
            "image": forms.FileInput()
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["location"].widget.attrs["id"] = "loc"

class TimeSlotForm(forms.ModelForm):
    class Meta:
        model = TimeSlot
        fields = ["time", "date"]

        widgets = {"time": TimeInput(), "date": DateInput()}

    def set_limits(self, event):
        self.fields["date"].widget.attrs["min"] = event.startdate
        self.fields["date"].widget.attrs["max"] = event.enddate
        self.fields["time"].widget.attrs["min"] = event.starttime
        self.fields["time"].widget.attrs["max"] = event.endtime

class NameForm(forms.Form):
    username = forms.CharField(label='Username', max_length=100)
    firstname = forms.CharField(label='First name', max_length=100)
    lastname = forms.CharField(label='Last name', max_length=100)
    email = forms.EmailField(label='Email', max_length=254)
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


