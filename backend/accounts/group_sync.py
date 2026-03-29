from __future__ import annotations

from .group_defaults import DEFAULT_SIGNUP_GROUP_NAMES, LEGACY_DEFAULT_GROUP_NAME
from .models import UserGroup, UserProfile


def sync_signup_groups() -> dict[str, object]:
    created_names: list[str] = []
    existing_names: list[str] = []

    for name in DEFAULT_SIGNUP_GROUP_NAMES:
        _, created = UserGroup.objects.get_or_create(name=name)
        if created:
            created_names.append(name)
        else:
            existing_names.append(name)

    removed_legacy = False
    legacy_group = UserGroup.objects.filter(name=LEGACY_DEFAULT_GROUP_NAME).first()
    if legacy_group and not UserProfile.objects.filter(group=legacy_group).exists():
        legacy_group.delete()
        removed_legacy = True

    return {
        "created_names": created_names,
        "existing_names": existing_names,
        "removed_legacy": removed_legacy,
        "legacy_name": LEGACY_DEFAULT_GROUP_NAME,
    }
