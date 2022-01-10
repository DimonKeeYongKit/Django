from django.contrib import admin
from .models import Venue, MyClubUser, Event
from django.contrib.auth.models import Group

@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'phone')
    ordering = ('name',)
    search_fields = ('name', 'address', 'phone')

admin.site.register(MyClubUser)

# Remove Groups
admin.site.unregister(Group)

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    fields = (('name', 'venue'), 'event_date', 'description', 'manager')
    list_display = ('name', 'event_date', 'venue')
    list_filter = ('event_date', 'venue')
    ordering = ('-event_date',)

