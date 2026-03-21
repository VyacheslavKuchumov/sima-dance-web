from django.contrib import admin
from django.contrib.admin.sites import NotRegistered
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from booking.models import Booking


User = get_user_model()


class BookingInline(admin.TabularInline):
    model = Booking
    fk_name = "user"
    extra = 0
    can_delete = False
    show_change_link = True
    verbose_name = "Бронирование"
    verbose_name_plural = "Что забронировал пользователь"
    fields = ("event", "seat", "status", "price_snapshot", "created_at", "expires_at")
    readonly_fields = fields
    ordering = ("-created_at",)

    def has_add_permission(self, request, obj=None):
        return False


try:
    admin.site.unregister(User)
except NotRegistered:
    pass


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    inlines = [BookingInline]
    list_display = DjangoUserAdmin.list_display + ("booking_count",)

    @admin.display(description="Бронирований")
    def booking_count(self, obj):
        return obj.bookings.count()
