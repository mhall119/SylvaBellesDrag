from random import choices
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _, pgettext_lazy as _p
from django.utils import timezone
from django.utils.functional import cached_property

import pytz
import datetime
from imagekit.models import ImageSpecField, ProcessedImageField
from imagekit.processors import Adjust, ColorOverlay, ResizeToFill, ResizeToFit, SmartResize
from imagekit import ImageSpec, register

from cities_light.models import City

# Create your models here.

class TimezoneChoices:
    def __iter__(self):
        for tz in pytz.all_timezones:
            yield (tz, tz)

class User(AbstractUser):
    # user = models.ForeignKey(User, on_delete=models.CASCADE)
    last_login = models.DateTimeField(blank=True, null=True)

class ProfilePhotos(ImageSpec):
    processors = [ResizeToFit(400, 300)]
    format = 'JPEG'
    options = {'quality': 60}
register.generator('dragme:profile_photo', ProfilePhotos)

class UploadedImage(models.Model):
    image = models.ImageField(upload_to='image_gallery')
    caption = models.CharField(max_length=256, null=True, blank=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

class Roles(models.IntegerChoices):
    PERFORMER = 1, _("Performer")
    DJ = 2, _("DJ")
    MUSICIAN = 3, _("Musician")
    KITTEN = 4, _("Kitten")
    
class Pronouns(models.TextChoices):
    HE = 'he', "He/Him/His"
    SHE = 'she', "She/Her/Hers"
    THEY = 'they', "They/Them/Theirs"
            
class Profile(models.Model):
    class Meta:
        ordering = ('name',)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    name = models.CharField(max_length=256, blank=False, null=False)
    website = models.URLField(blank=True, null=True)
    twitter = models.CharField(max_length=32, blank=True, null=True)
    instagram = models.CharField(max_length=32, blank=True, null=True)
    tiktok = models.CharField(max_length=32, blank=True, null=True)
    venmo = models.CharField(max_length=32, blank=True, null=True)
    cashapp = models.CharField(max_length=32, blank=True, null=True)

    tz = models.CharField(
        max_length=32,
        verbose_name=_("Timezone"),
        default="UTC",
        choices=TimezoneChoices(),
        blank=False,
        null=False,
    )
    avatar = ProcessedImageField(
        verbose_name=_("Profile Icon"),
        upload_to="avatars",
        processors=[SmartResize(512, 512)],
        format="PNG",
        blank=True,
    )
    profile = ProcessedImageField(
        verbose_name=_("Profile Picture"),
        upload_to="profiles",
        processors=[SmartResize(768, 1024)],
        format="PNG",
        blank=True,
    )
    city = models.ForeignKey(
        City,
        verbose_name=_("Home city"),
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    pronouns = models.CharField(choices=Pronouns.choices, default=Pronouns.SHE, max_length=32)

    children = models.ManyToManyField('Profile', related_name='parents', through='Lineage', through_fields=('parent', 'child'))
    gallery = models.ManyToManyField(UploadedImage, blank=True)

    active = models.BooleanField(default=True)

    def avatar_icon(self):
        try:
            return self.avatar.url
        except:
            return '/static/user-default.png'

    def upcoming_events(self):
        return Event.objects.filter(status=Event.CONFIRMED, lineup__performer=self, lineup__status=Talent.Statuses.CONFIRMED, end_time__gt=datetime.datetime.now()).order_by('start_time')

    def past_events(self):
        return Event.objects.filter(status=Event.CONFIRMED, lineup__performer=self, lineup__status=Talent.Statuses.CONFIRMED, end_time__lt=datetime.datetime.now()).order_by('-end_time')

    @property
    def they(self):
        if self.pronouns == Pronouns.HE:
            return 'he'
        elif self.pronouns == Pronouns.SHE:
            return 'she'
        else:
            return 'they'
            
    @property
    def them(self):
        if self.pronouns == Pronouns.HE:
            return 'him'
        elif self.pronouns == Pronouns.SHE:
            return 'her'
        else:
            return 'them'
            
    @property
    def their(self):
        if self.pronouns == Pronouns.HE:
            return 'his'
        elif self.pronouns == Pronouns.SHE:
            return 'her'
        else:
            return 'their'

    def __str__(self):
        return self.name

class Lineage(models.Model):
    parent = models.ForeignKey(Profile, related_name='descendants', on_delete=models.CASCADE)
    child = models.ForeignKey(Profile, related_name='ancestors', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.parent} -> {self.child}'

class House(models.Model):
    name = models.CharField(max_length=256)
    head = models.ForeignKey(Profile, related_name='head_of', on_delete=models.SET_NULL, null=True, blank=True)
    members = models.ManyToManyField(Profile, related_name='houses', through='HouseMembership', through_fields=('house', 'member'))
    logo = ProcessedImageField(
        verbose_name=_("Logo"),
        upload_to="house_logos",
        processors=[ResizeToFill(256, 256)],
        format="PNG",
        blank=True,
    )
    banner = ProcessedImageField(
        verbose_name=_("Banner Image"),
        upload_to="house_banners",
        processors=[ResizeToFill(256, 1024)],
        format="PNG",
        blank=True,
    )

    def __str__(self):
        return self.name

class HouseMembership(models.Model):
    house = models.ForeignKey(House, related_name='membership', on_delete=models.CASCADE)
    member = models.ForeignKey(Profile, related_name='membership', on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.house} [{self.member}]'

class Venue(models.Model):
    name = models.CharField(help_text=_("Name of the Venue"), max_length=150)
    city = models.ForeignKey(City, verbose_name=_("City"), on_delete=models.CASCADE)
    address = models.CharField(
        help_text=_("Address with Street and Number"),
        max_length=150,
        null=True,
        blank=True,
    )
    latitude = models.FloatField(
        help_text=_("Latitude in Degrees North"), null=True, blank=True
    )
    longitude = models.FloatField(
        help_text=_("Longitude in Degrees East"), null=True, blank=True
    )
    tz = models.CharField(
        max_length=32,
        verbose_name=_("Timezone"),
        default="UTC",
        choices=TimezoneChoices(),
        blank=False,
        null=False,
    )
    venue_website = models.URLField(
        help_text=_("Link to the Venue's Website"),
        verbose_name=_("Website"),
        max_length=200,
        blank=True,
        null=True,
    )

    def __str__(self):
        return f'{self.name} in {self.city.name}'

class Show(models.Model):
    name = models.CharField(max_length=256, verbose_name=_('Show Name'))
    runner = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True)
    summary = models.TextField(
        help_text=_("Markdown formatting supported"), blank=True, null=True
    )
    logo = ProcessedImageField(
        verbose_name=_("Logo"),
        upload_to="house_logos",
        processors=[ResizeToFill(256, 256)],
        format="PNG",
        blank=True,
    )
    banner = ProcessedImageField(
        verbose_name=_("Banner Image"),
        upload_to="house_banners",
        processors=[ResizeToFill(768, 1024)],
        format="PNG",
        blank=True,
    )
    default_city = models.ForeignKey(
        City,
        verbose_name=_("Home city"),
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    default_venue = models.ForeignKey(
        Venue,
        verbose_name=_('Default Venue'),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    website = models.URLField(blank=True, null=True)
    twitter = models.CharField(max_length=32, blank=True, null=True)
    instagram = models.CharField(max_length=32, blank=True, null=True)
    hashtag = models.CharField(max_length=32, blank=True, null=True)
    venmo = models.CharField(max_length=32, blank=True, null=True)
    cashapp = models.CharField(max_length=32, blank=True, null=True)

    gallery = models.ManyToManyField(UploadedImage, blank=True)

    active = models.BooleanField(default=True)

    @cached_property
    def next_event(self):
        return Event.objects.filter(show=self, end_time__gte=datetime.datetime.utcnow()).order_by('start_time').first()

    def __str__(self):
        return self.name

class Event(models.Model):
    class Meta:
        ordering = ['-start_time']
        
    CANCELED = -1
    PLANNING = 0
    CONFIRMED = 1

    STATUSES = [
        (CANCELED, _("Canceled")),
        (PLANNING, _("Planning")),
        (CONFIRMED, _("Confirmed")),
    ]
    name = models.CharField(max_length=150, verbose_name=_("Event Name"))
    host = models.ForeignKey(Profile, related_name='hosting',  on_delete=models.CASCADE)
    show = models.ForeignKey(
        Show,
        related_name="events",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    status = models.SmallIntegerField(
        choices=STATUSES, default=CONFIRMED, db_index=True
    )
    start_time = models.DateTimeField(verbose_name=_("Start Time"), db_index=True)
    end_time = models.DateTimeField(verbose_name=_("End Time"), db_index=True)

    summary = models.TextField(
        help_text=_("Markdown formatting supported"), blank=True, null=True
    )

    venue = models.ForeignKey(Venue, blank=True, null=True, on_delete=models.SET_NULL)

    event_url = models.URLField(
        verbose_name=_("Event Website"), help_text=_("Link to the Event's website"), max_length=200, blank=True, null=True
    )

    poster = ProcessedImageField(
        verbose_name=_("Promo Image"),
        upload_to="event_promos",
        processors=[ResizeToFit(512, 1024)],
        format="PNG",
        blank=True,
    )

    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_time = models.DateTimeField(
        help_text=_("the date and time when the event was created"),
        default=timezone.now,
        db_index=True,
    )

    website = models.URLField(blank=True, null=True)
    twitter = models.CharField(max_length=32, blank=True, null=True)
    instagram = models.CharField(max_length=32, blank=True, null=True)
    hashtag = models.CharField(max_length=32, blank=True, null=True)
    venmo = models.CharField(max_length=32, blank=True, null=True)
    cashapp = models.CharField(max_length=32, blank=True, null=True)

    gallery = models.ManyToManyField(UploadedImage, blank=True)

    @property
    def poster_url(self):
        if self.poster:
            return self.poster.url
        elif self.show.banner:
            return self.show.banner.url
        else:
            return None

    @cached_property
    def performers(self):
        return [t.performer for t in Talent.objects.filter(event=self, role=Roles.PERFORMER, status=Talent.Statuses.CONFIRMED)]

    @property
    def musicians(self):
        return [t.performer for t in Talent.objects.filter(event=self, role=Roles.MUSICIAN, status=Talent.Statuses.CONFIRMED)]

    @property
    def djs(self):
        return [t.performer for t in Talent.objects.filter(event=self, role=Roles.DJ, status=Talent.Statuses.CONFIRMED)]

    def __str__(self):
        return f'{self.name} on {self.start_time.date()} at {self.venue}'

class Talent(models.Model):
    class Meta:
        verbose_name_plural = _('talent')
        ordering = ('event__start_time', 'status')

    class Statuses(models.IntegerChoices):
        CANCELED = -1, _('Canceled')
        PLANNING = 0, _('Planning')
        CONFIRMED = 1, _('Confirmed')
    
    event = models.ForeignKey(Event, related_name='lineup', on_delete=models.CASCADE)
    performer = models.ForeignKey(Profile, related_name='schedule', on_delete=models.CASCADE)
    role = models.SmallIntegerField(
        choices=Roles.choices, default=Roles.PERFORMER
    )
    status = models.SmallIntegerField(
        choices=Statuses.choices, default=Statuses.CONFIRMED
    )

    def __str__(self):
        return f'{self.performer} as {self.get_role_display()} at {self.event} ({self.get_status_display()})'