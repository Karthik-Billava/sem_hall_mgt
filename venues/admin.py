from django.contrib import admin
from .models import Venue, VenueImage, Availability

class VenueImageInline(admin.TabularInline):
    model = VenueImage
    extra = 1

class AvailabilityInline(admin.TabularInline):
    model = Availability
    extra = 1

@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'capacity', 'hourly_rate', 'manager', 'is_active')
    list_filter = ('is_active', 'city', 'has_projector', 'has_sound_system', 'has_wifi', 'has_catering', 'has_parking', 'has_air_conditioning')
    search_fields = ('name', 'description', 'address', 'city', 'state')
    inlines = [VenueImageInline, AvailabilityInline]

@admin.register(VenueImage)
class VenueImageAdmin(admin.ModelAdmin):
    list_display = ('venue', 'is_primary', 'uploaded_at')
    list_filter = ('is_primary', 'uploaded_at')
    search_fields = ('venue__name',)

@admin.register(Availability)
class AvailabilityAdmin(admin.ModelAdmin):
    list_display = ('venue', 'date', 'start_time', 'end_time', 'is_available')
    list_filter = ('is_available', 'date')
    search_fields = ('venue__name',) 