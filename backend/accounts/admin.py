from django.contrib import admin
from django.contrib.admin.sites import NotRegistered
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from accounts.models import UserGroup, UserProfile
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


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    fk_name = "user"
    extra = 0
    can_delete = False
    fields = ("group", "full_name", "child_full_name", "created_at", "updated_at")
    readonly_fields = ("created_at", "updated_at")

    def has_add_permission(self, request, obj=None):
        return False


try:
    admin.site.unregister(User)
except NotRegistered:
    pass


@admin.register(UserGroup)
class UserGroupAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    inlines = [BookingInline, UserProfileInline]
    list_display = DjangoUserAdmin.list_display + ("booking_count",)

    @admin.display(description="Бронирований")
    def booking_count(self, obj):
        return obj.bookings.count()
