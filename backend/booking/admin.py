from django.contrib import admin
from .models import Event, Seat, Booking


# Register your models here.

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "starts_at", "archived", "created_at")
    list_filter = ("archived", "starts_at")
    search_fields = ("title",)
    ordering = ("-starts_at",)


@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display = ("id", "section", "row", "number", "price")
    list_filter = ("section",)
    search_fields = ("section", "row", "number", "price")
    ordering = ("section", "row", "number", "price")


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "event", "seat", "status", "created_at", "expires_at", "price_snapshot")
    list_filter = ("status", "event")
    search_fields = ("user__username", "seat__row", "seat__number")
    ordering = ("-created_at",)
    autocomplete_fields = ("user", "event", "seat")
