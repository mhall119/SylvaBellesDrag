from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

# Register your models here.

@admin.register(User)
class UserAdmin(UserAdmin):

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('', {'fields': ('last_login',)}),
    )

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    raw_id_fields = ('city',)

admin.register(Lineage)(admin.ModelAdmin)

admin.register(House)(admin.ModelAdmin)

admin.register(HouseMembership)(admin.ModelAdmin)

@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    raw_id_fields = ('city',)

@admin.register(Show)
class ShowAdmin(admin.ModelAdmin):
    raw_id_fields = ('default_city',)

class TalentInline(admin.TabularInline):
    model = Talent
    extras = 10

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    inlines = [TalentInline,]
    list_filter = ('show', 'start_time', 'status')
    list_display = ('name', 'show', 'start_time', 'venue', 'status')

admin.register(Talent)(admin.ModelAdmin)
