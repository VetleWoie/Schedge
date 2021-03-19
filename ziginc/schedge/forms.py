from django import forms
from itertools import product
import datetime as dt
from django.forms.widgets import TextInput
from django.utils.dateparse import parse_duration
from django.core.exceptions import ValidationError
from django.forms.widgets import MultiWidget
from .models import Event, TimeSlot
from django.contrib.auth.models import User
from .widgets import SplitDurationWidget, MultiValueDurationField

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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['duration'] = MultiValueDurationField()
        self.fields["starttime"].initial = "08:00"
        self.fields["endtime"].initial = "16:00"

    class Meta:
        model = Event
        fields = [
            "title",
            "location",
            "startdate",
            "enddate",
            "starttime",
            "endtime",
            "duration",
            "description",
            "image",
        ]

        labels = {
            "startdate": "Start Date",
            "enddate": "End Date",
            "starttime": "Start Time",
            "endtime": "End Time"
        }

        today = dt.datetime.today().strftime("%Y-%m-%d")

        widgets = {
            "startdate": DateInput(attrs={"min": today, "max": max_date()}),
            "enddate": DateInput(attrs={"min": today, "max": max_date()}),
            "starttime": TimeInput(format=("HH:mm")),
            "endtime": TimeInput(format=("HH:mm")),
            "image": forms.FileInput(),
        }

class TimeSlotForm(forms.ModelForm):
    class Meta:
        model = TimeSlot
        fields = ["start_time", "end_time", "date"]

        widgets = {"start_time": TimeInput(), "end_time": TimeInput(), "date": DateInput()}
    def __init__(self, *args, **kwargs):
        self.duration = kwargs.pop("duration", None)
        super().__init__(*args, **kwargs)

    def set_limits(self, event):
        self.fields["date"].widget.attrs["min"] = event.startdate
        self.fields["date"].widget.attrs["max"] = event.enddate
        self.fields["start_time"].widget.attrs["min"] = event.starttime
        self.fields["start_time"].widget.attrs["max"] = event.endtime
        self.fields["end_time"].widget.attrs["min"] = event.starttime
        self.fields["end_time"].widget.attrs["max"] = event.endtime
    def clean(self):
        start = dt.datetime.combine(self.cleaned_data.get("date"), self.cleaned_data.get("start_time"))
        end = dt.datetime.combine(self.cleaned_data.get("date"), self.cleaned_data.get("end_time"))
        if end - start < self.duration:
            raise forms.ValidationError(
                {
                    "start_time": ["Time slot is too short"],
                    "end_time": ["Time slot is too short"],
                }
            )
        return self.cleaned_data
        




class NameForm(forms.Form):
    username = forms.CharField(
        label="Username",
        max_length=100,
        widget=forms.TextInput(attrs={"autofocus": "autofocus"}),
    )
    first_name = forms.CharField(label="First name", max_length=100)
    last_name = forms.CharField(label="Last name", max_length=100)
    email = forms.EmailField(label="Email", max_length=254)
    password = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Rewrite password", widget=forms.PasswordInput)

    def clean(self):
        # Check that passwords match
        password = self.cleaned_data.get("password")
        password2 = self.cleaned_data.get("password2")
        if password and password != password2:
            raise forms.ValidationError("Passwords don't match.")
        return self.cleaned_data

    def clean_username(self):
        # Check that username hasn't been used before
        username = self.cleaned_data["username"]
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username already taken.")
        return username

    def clean_email(self):
        # Check that email is unique
        email = self.cleaned_data["email"]
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email is already in use.")
        return email


class InviteForm(forms.Form):
    invitee = forms.ModelChoiceField(
        queryset=User.objects.exclude(is_superuser=True).order_by("username")
    )

    def __init__(self, *args, **kwargs):
        invites = kwargs.pop("invites", None)
        if invites is not None:
            invited_ids = invites.values_list("invitee", flat=True)
            invited_names = User.objects.filter(id__in=invited_ids).values_list("username", flat=True)
        
        accepted = kwargs.pop("accepted", None)
        if accepted is not None:
            accepted_ids = accepted.values_list("user", flat=True)
            accepted_names = User.objects.filter(id__in=accepted_ids).values_list("username", flat=True)

        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if invites is None or accepted is None or user is None:
            return

        excluded = invited_names | accepted_names

        # remove yourself from choises
        choices = self.fields["invitee"].choices
        self.fields["invitee"].choices = [
            (v, u) for v, u in choices if u not in excluded and u != user.username
        ]
