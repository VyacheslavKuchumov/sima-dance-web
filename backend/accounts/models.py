from django.conf import settings
from django.db import models


User = settings.AUTH_USER_MODEL


class UserGroup(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name="profile", on_delete=models.CASCADE)
    group = models.ForeignKey(UserGroup, related_name="profiles", on_delete=models.PROTECT)
    full_name = models.CharField(max_length=255)
    child_full_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["user__username"]

    def __str__(self):
        return f"{self.user} - {self.group}"
