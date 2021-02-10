from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponseNotFound, HttpResponseBadRequest

from .forms import EventForm
from .models import Event

# Create your views here.

def create_event(request):
    if request.method == 'POST':
        # pressed submit

        # get info in the form
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            data = form.cleaned_data
            # create new event with stuff in form
            # because EventForm is model of Event, we can safely use kwargs
            print(data)
            newevent = Event.objects.create(**data)
            return redirect(event, newevent.id)
        else:
            return HttpResponseBadRequest("Invalid Form!")

    # GET
    form = EventForm()  # empty form
    context = {'form': form}
    return render(request, 'createevent.html', context)

def event(request, event_id):
    try:
        # select * from Event where id=event_id;
        event = Event.objects.get(id=event_id)
    except Event.DoesNotExist:
        return HttpResponseNotFound("404: not valid event id")


    context = {'event': event}
    return render(request, 'event.html', context)
