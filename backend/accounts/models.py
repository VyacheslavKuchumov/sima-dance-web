from django.conf import settings
from django.db import models


User = settings.AUTH_USER_MODEL


class UserGroup(models.Model):
    name = models.CharField("Название", max_length=255, unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Группа пользователей"
        verbose_name_plural = "Группы пользователей"

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name="profile", on_delete=models.CASCADE, verbose_name="Пользователь")
    group = models.ForeignKey(UserGroup, related_name="profiles", on_delete=models.PROTECT, verbose_name="Группа")
    full_name = models.CharField("ФИО пользователя", max_length=255)
    child_full_name = models.CharField("ФИО ребенка", max_length=255)
    created_at = models.DateTimeField("Создано", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлено", auto_now=True)

    class Meta:
        ordering = ["user__username"]
        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профили пользователей"

    def __str__(self):
        return f"{self.user} - {self.group}"
