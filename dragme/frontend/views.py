from django.http import HttpResponse, Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count, Max
from django.db.models.functions import Lower
from django.contrib.auth import authenticate, login as login_user, logout as logout_user
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UsernameField, SetPasswordForm
from django.contrib import messages
from django import forms

from django.db.models import Max, F, Q
import datetime

from core.models import *

# Create your views here.

class NewUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "email")
        field_classes = {'username': UsernameField}

    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)
        self.fields['email'].required = True

def login(request):
    next_view = 'manage_shows'
    if 'next' in request.GET:
        next_view = request.GET.get('next', 'manage_shows')

    if request.user.is_authenticated:
        return redirect(next_view)

    context = {
        "signup_form":  NewUserForm(),
        "login_form": AuthenticationForm(),
    }
    if request.method == "POST":
        if request.POST.get("action") == "login":
            login_form = AuthenticationForm(data=request.POST)
            if login_form.is_valid():
                username = login_form.cleaned_data.get("username")
                raw_password = login_form.cleaned_data.get("password")
                user = authenticate(username=username, password=raw_password)
                login_user(request, user, backend=user.backend)
                try:
                    return redirect(next_view)
                except:
                    raise Http404("Page does not exist")
            else:
                context["login_form"] = login_form
                context["action"] = "login"
        elif request.POST.get("action") == "signup":
            signup_form = NewUserForm(data=request.POST)
            if signup_form.is_valid():
                signup_form.save()
                username = signup_form.cleaned_data.get("username")
                raw_password = signup_form.cleaned_data.get("password1")
                user = authenticate(username=username, password=raw_password)
                login_user(request, user, backend=user.backend)
                try:
                    return redirect(next_view)
                except:
                    raise Http404("Page does not exist")
            else:
                context["signup_form"] = signup_form
                context["action"] = "signup"

    return render(request, 'login.html', context)

def get_user_shows(user):
    my_shows = Show.objects.all()
    if not user.is_superuser:
        my_shows = my_shows.filter(profile__user=user)
    return my_shows

@login_required
def manage_shows(request):
    my_shows = get_user_shows(request.user)

    first = my_shows.first()
    if first:
        return redirect('manage_show', show_id=first.id)
    else:
        return Http404()

class ShowForm(forms.ModelForm):
    class Meta:
        model = Show
        fields = ('name', 'banner', 'default_venue', 'active', 'summary', 'instagram', 'twitter', 'hashtag', 'venmo', 'cashapp')

@login_required
def edit_show(request, show_id):
    show = get_object_or_404(Show, id=show_id)
    if show.runner.user is not request.user and not request.user.is_superuser:
        return Http404()

    if request.method == 'POST':
        form = ShowForm(instance=show, data=request.POST, files=request.FILES)
        if form.is_valid():
            new_show = form.save()
            return redirect('manage_show', show_id=new_show.id)
    else:
        form = ShowForm(instance=show)

    my_shows = get_user_shows(request.user)
    context = {
        'active_show': show,
        'show_form': form,
        'shows': my_shows,
    }
    return render(request, 'edit_show.html', context)

@login_required
def manage_show(request, show_id):
    show = get_object_or_404(Show, id=show_id)
    if show.runner.user is not request.user and not request.user.is_superuser:
        return Http404()

    my_shows = get_user_shows(request.user)
    context = {
        'active_show': show,
        'shows': my_shows,
    }
    return render(request, 'manage_show.html', context)

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ('name', 'host', 'status', 'start_time', 'end_time', 'venue', 'summary', 'event_url', 'poster', 'instagram', 'twitter', 'hashtag', 'venmo', 'cashapp')
        widgets = {
            'start_time': forms.DateTimeInput(format="%Y-%m-%dT%H:%M", attrs={'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(format="%Y-%m-%dT%H:%M", attrs={'type': 'datetime-local'}),
        }

@login_required
def add_event(request, show_id):
    show = get_object_or_404(Show, id=show_id)
    if show.runner.user is not request.user and not request.user.is_superuser:
        return Http404()

    event = Event(show=show, created_by=request.user, host=show.runner, venue=show.default_venue)

    if request.method == 'POST':
        form = EventForm(instance=event, data=request.POST, files=request.FILES)
        if form.is_valid():
            new_event = form.save()
            return redirect('manage_event', show_id=new_event.show.id, event_id=new_event.id)
    else:
        form = EventForm(instance=event)

    my_shows = get_user_shows(request.user)
    context = {
        'active_show': show,
        'active_event': event,
        'event_form': form,
        'shows': my_shows,
    }
    return render(request, 'add_event.html', context)

@login_required
def edit_event(request, show_id, event_id):
    event = get_object_or_404(Event, id=event_id, show_id=show_id)
    show = event.show
    if show.runner.user is not request.user and not request.user.is_superuser:
        return Http404()

    if request.method == 'POST':
        form = EventForm(instance=event, data=request.POST, files=request.FILES)
        if form.is_valid():
            new_event = form.save()
            return redirect('manage_event', show_id=new_event.show.id, event_id=new_event.id)
    else:
        form = EventForm(instance=event)

    my_shows = get_user_shows(request.user)
    context = {
        'active_show': show,
        'active_event': event,
        'event_form': form,
        'shows': my_shows,
    }
    return render(request, 'edit_event.html', context)

@login_required
def delete_event(request, show_id, event_id):
    event = get_object_or_404(Event, id=event_id, show_id=show_id)
    show = event.show
    if show.runner.user is not request.user and not request.user.is_superuser:
        return Http404()

    if request.method == 'POST':
        event.delete()
        return redirect(manage_show, show_id=show.id)

    my_shows = get_user_shows(request.user)
    context = {
        'active_show': show,
        'active_event': event,
        'shows': my_shows,
    }
    return render(request, 'delete_event.html', context)

@login_required
def manage_event(request, show_id, event_id):
    event = get_object_or_404(Event, id=event_id, show_id=show_id)
    show = event.show
    if show.runner.user is not request.user and not request.user.is_superuser:
        return Http404()

    my_shows = get_user_shows(request.user)
    context = {
        'active_event': event,
        'active_show': show,
        'shows': my_shows,
    }
    return render(request, 'manage_event.html', context)

class TalentForm(forms.ModelForm):
    class Meta:
        model = Talent
        fields = ('performer', 'role', 'status')

@login_required
def add_talent(request, show_id, event_id):
    event = get_object_or_404(Event, id=event_id, show_id=show_id)
    show = event.show
    if show.runner.user is not request.user and not request.user.is_superuser:
        return Http404()

    talent = Talent(event=event)

    if request.method == 'POST':
        form = TalentForm(instance=talent, data=request.POST, files=request.FILES)
        if form.is_valid():
            new_talent = form.save()
            return redirect('manage_event', show_id=event.show.id, event_id=event.id)
    else:
        form = TalentForm(instance=event)

    my_shows = get_user_shows(request.user)
    context = {
        'active_show': show,
        'active_event': event,
        'active_talent': talent,
        'talent_form': form,
        'shows': my_shows,
    }
    return render(request, 'add_talent.html', context)

@login_required
def edit_talent(request, show_id, event_id, talent_id):
    talent = get_object_or_404(Talent, id=talent_id, event_id=event_id, event__show_id=show_id)
    event = talent.event
    show = event.show
    if show.runner.user is not request.user and not request.user.is_superuser:
        return Http404()

    if request.method == 'POST':
        form = TalentForm(instance=talent, data=request.POST, files=request.FILES)
        if form.is_valid():
            new_talent = form.save()
            return redirect('manage_event', show_id=event.show.id, event_id=event.id)
    else:
        form = TalentForm(instance=talent)

    my_shows = get_user_shows(request.user)
    context = {
        'active_show': show,
        'active_event': event,
        'active_talent': talent,
        'talent_form': form,
        'shows': my_shows,
    }
    return render(request, 'edit_talent.html', context)

@login_required
def delete_talent(request, show_id, event_id, talent_id):
    talent = get_object_or_404(Talent, id=talent_id, event_id=event_id, event__show_id=show_id)
    event = talent.event
    show = event.show
    if show.runner.user is not request.user and not request.user.is_superuser:
        return Http404()

    if request.method == 'POST':
        talent.delete()
        return redirect(manage_event, show_id=show.id, event_id=event.id)

    my_shows = get_user_shows(request.user)
    context = {
        'active_show': show,
        'active_event': event,
        'active_talent': talent,
        'shows': my_shows,
    }
    return render(request, 'delete_talent.html', context)

# class PasswordResetRequestForm(forms.Form):
#     email = forms.EmailField(
#         label="Email",
#         max_length=254,
#         widget=forms.EmailInput(attrs={'autocomplete': 'email'})
#     )

# def password_reset_request(request):
#     context = {}
#     if request.method == "POST":
#         form = PasswordResetRequestForm(data=request.POST)
#         if form.is_valid():
#             email = form.cleaned_data['email']
#             PasswordResetRequest.send(email)
#             messages.success(request, "Password reset email sent")
#             return redirect("login")
#         else:
#             messages.error(request, "Invalid emails")

#     else:
#         form = PasswordResetRequestForm()

#     context['form'] = form
#     return render(request, 'savannahv2/password_reset.html', context)


# def reset_password(request, request_key):
#     try:
#         reset = PasswordResetRequest.objects.get(key=request_key)
#         if reset.expires >= datetime.datetime.utcnow():
#             if request.method == "POST":
#                 form = SetPasswordForm(user=reset.user, data=request.POST)
#                 if form.is_valid():
#                     user = form.save()
#                     login_user(request, user)
#                     messages.success(request, "Your password has been reset")
#                     reset.delete()
#                     return redirect('home')
#             else:
#                 form = SetPasswordForm(user=reset.user)

#             context = {
#                 'form': form
#             }
#             return render(request, 'savannahv2/password_reset.html', context)
#         else:
#             messages.error(request, "Your password reset request has expired")
#     except:
#         messages.error(request, "Invalid reset request")
#     return redirect('login')

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
    performers = Profile.objects.filter(active=True)
    performers = performers.annotate(last_show=Max('schedule__event__start_time', filter=Q(schedule__event__start_time__lte=as_of_date, schedule__status=Talent.Statuses.CONFIRMED, schedule__role=Roles.PERFORMER)))
    performers = performers.filter(last_show__isnull=False).order_by('-last_show', 'name')

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
