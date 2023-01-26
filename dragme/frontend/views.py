from django.shortcuts import render, get_object_or_404
from django.db.models import Max, F, Q
import datetime

from core.models import *

# Create your views here.

def home(request):
    context = {
        'next_event': Event.objects.filter(end_time__gte=datetime.datetime.utcnow() - datetime.timedelta(days=1)).order_by('start_time').first()
    }
    return render(request, 'index.html', context)

def event(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    context = {
        'event': event,
    }
    return render(request, 'event.html', context)

def shows(request):
    shows = Show.objects.filter(active=True)
    context = {
        'shows': shows,
    }
    return render(request, 'shows.html', context)

def performers(request):
    next_event = Event.objects.filter(end_time__gte=datetime.datetime.utcnow() - datetime.timedelta(days=1)).order_by('start_time').first()
    if next_event:
        as_of_date = next_event.start_time
    else:
        as_of_date = datetime.datetime.utcnow()
    performers = Profile.objects.filter(active=True).annotate(last_show=Max('schedule__event__start_time', filter=Q(schedule__event__start_time__lte=as_of_date, schedule__status=Talent.Statuses.CONFIRMED))).order_by(F('last_show').desc(nulls_last=True), 'name')

    context = {
        'performers': performers,
    }
    return render(request, 'performers.html', context)

def profile(request, profile_id):
    profile = get_object_or_404(Profile, id=profile_id)
    context = {
        'profile': profile,
    }
    return render(request, 'profile.html', context)

def store(request):

    context = {
    }
    return render(request, 'store.html', context)
