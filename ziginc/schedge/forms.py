from django import forms
from itertools import product
import datetime as dt

from .models import Event, TimeSlot

class DateInput(forms.DateInput):
    input_type = 'date'


class TimeInput(forms.DateInput):
    input_type = 'time'


def max_date(years=10):
    """Returns the date in 10 years
    If leap day (29-02), return (28-02)"""
    today = dt.datetime.today()
    maxyear = today.year + years
    maxmonth = today.month

    # 28 on Feb 29 (leap day). 10 years after leap day is not leap year
    maxday = today.day if today.day != 29 or today.month != 2 else 28
    return dt.datetime(maxyear, maxmonth, maxday).strftime('%Y-%m-%d')


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'startdate', 'enddate', 'description', 'starttime', 'endtime', 'duration', 'location', 'image']
        
        today = dt.datetime.today().strftime('%Y-%m-%d')

        widgets = {
            'startdate': DateInput(
                attrs={'min': today, 'max': max_date()}
            ),
            'enddate': DateInput(
                attrs={'min': today, 'max': max_date()}
            ),
            'starttime': TimeInput(),
            'endtime': TimeInput(),
            
            # 'duration': DateInput(attrs={'class':'timepicker'})

        }


class TimeSlotForm(forms.ModelForm):
    class Meta:
        model = TimeSlot
        fields = ['time', 'date']

        widgets = {
            'time': TimeInput(),
            'date': DateInput()
        }
