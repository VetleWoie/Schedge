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
        fields = ["start_time", "end_time", "date"]

        widgets = {"start_time": TimeInput(), "end_time": TimeInput(), "date": DateInput()}
    def __init__(self, event="", user="", *args, **kwargs):
        self.user = user
        self.event = event
        super(TimeSlotForm, self).__init__(*args, **kwargs)

    def set_limits(self, event):
        self.fields["date"].widget.attrs["min"] = event.startdate
        self.fields["date"].widget.attrs["max"] = event.enddate
        self.fields["start_time"].widget.attrs["min"] = event.starttime
        self.fields["start_time"].widget.attrs["max"] = event.endtime
        self.fields["end_time"].widget.attrs["min"] = event.starttime
        self.fields["end_time"].widget.attrs["max"] = event.endtime

    # Check if time slot intersects with other timeslots from the same user
    def clean(self):
        start =  self.cleaned_data["start_time"]
        end =  self.cleaned_data["end_time"]
        date =  self.cleaned_data["date"]
        user_ts = TimeSlot.objects.filter(event=self.event, creator=self.user)
        for ts in user_ts:
            if not (ts.start_time > end or ts.end_time < start or date != ts.date): # Check if intersection exists
                raise forms.ValidationError("This timeslot is already selected")
        return self.cleaned_data

class NameForm(forms.Form):
    username = forms.CharField(label='Username', max_length=100, widget=forms.TextInput(attrs={'autofocus': 'autofocus'}))
    first_name = forms.CharField(label='First name', max_length=100)
    last_name = forms.CharField(label='Last name', max_length=100)
    email = forms.EmailField(label='Email', max_length=254)
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Rewrite password', widget=forms.PasswordInput)
    
    def clean(self):
        #Check that passwords match
        password = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password2')
        if password and password != password2:
            raise forms.ValidationError("Passwords don't match.")
        return self.cleaned_data

    def clean_username(self):
        #Check that username hasn't been used before
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username already taken.")
        return username

    def clean_email(self):
        #Check that email is unique
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email is already in use.")
        return email


