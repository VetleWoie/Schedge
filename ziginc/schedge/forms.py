from django import forms
from itertools import product
import datetime as dt
from django.forms.widgets import TextInput
from django.utils.dateparse import parse_duration

from django.forms.widgets import MultiWidget
from .models import Event, TimeSlot
from durationwidget.widgets import TimeDurationWidget


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
