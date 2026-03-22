from django.contrib import admin
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone

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
    list_display = (
        "id",
        "user",
        "user_full_name",
        "child_full_name",
        "user_group",
        "event",
        "seat",
        "status",
        "is_paid",
        "is_ticket_issued",
        "created_at",
        "expires_at",
        "price_snapshot",
    )
    list_filter = ("status", "event", "is_paid", "is_ticket_issued", "user__profile__group")
    search_fields = (
        "user__username",
        "user__profile__full_name",
        "user__profile__child_full_name",
        "user__profile__group__name",
        "seat__row",
        "seat__number",
        "event__title",
    )
    ordering = ("-created_at",)
    autocomplete_fields = ("user", "event", "seat")
    actions = ("mark_as_paid", "mark_as_unpaid", "mark_ticket_issued", "mark_ticket_not_issued")
    list_select_related = ("user__profile__group", "event", "seat")

    def _get_profile(self, obj):
        try:
            return obj.user.profile
        except ObjectDoesNotExist:
            return None

    @admin.display(description="ФИО", ordering="user__profile__full_name")
    def user_full_name(self, obj):
        profile = self._get_profile(obj)
        return profile.full_name if profile else ""

    @admin.display(description="ФИО ребенка", ordering="user__profile__child_full_name")
    def child_full_name(self, obj):
        profile = self._get_profile(obj)
        return profile.child_full_name if profile else ""

    @admin.display(description="Группа", ordering="user__profile__group__name")
    def user_group(self, obj):
        profile = self._get_profile(obj)
        return getattr(profile.group, "name", "") if profile and profile.group_id else ""

    @admin.action(description="Отметить как оплаченные")
    def mark_as_paid(self, request, queryset):
        updated = queryset.update(is_paid=True, updated_at=timezone.now())
        self.message_user(request, f"Отмечено как оплаченные: {updated}")

    @admin.action(description="Снять отметку оплаты")
    def mark_as_unpaid(self, request, queryset):
        updated = queryset.update(is_paid=False, updated_at=timezone.now())
        self.message_user(request, f"Снята отметка оплаты: {updated}")

    @admin.action(description="Отметить билет как выписанный")
    def mark_ticket_issued(self, request, queryset):
        updated = queryset.update(is_ticket_issued=True, updated_at=timezone.now())
        self.message_user(request, f"Билетов отмечено как выписанные: {updated}")

    @admin.action(description="Снять отметку выписки билета")
    def mark_ticket_not_issued(self, request, queryset):
        updated = queryset.update(is_ticket_issued=False, updated_at=timezone.now())
        self.message_user(request, f"Снята отметка выписки билета: {updated}")
