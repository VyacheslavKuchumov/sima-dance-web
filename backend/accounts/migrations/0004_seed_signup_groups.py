from django.db import migrations


DEFAULT_SIGNUP_GROUP_NAMES = [
    *(f"{index} группа" for index in range(1, 11)),
    "соло",
    "дуэты",
]
LEGACY_DEFAULT_GROUP_NAME = "Основная группа"


def seed_signup_groups(apps, schema_editor):
    UserGroup = apps.get_model("accounts", "UserGroup")
    UserProfile = apps.get_model("accounts", "UserProfile")

    for name in DEFAULT_SIGNUP_GROUP_NAMES:
        UserGroup.objects.get_or_create(name=name)

    legacy_group = UserGroup.objects.filter(name=LEGACY_DEFAULT_GROUP_NAME).first()
    if legacy_group and not UserProfile.objects.filter(group=legacy_group).exists():
        legacy_group.delete()


def unseed_signup_groups(apps, schema_editor):
    UserGroup = apps.get_model("accounts", "UserGroup")
    UserProfile = apps.get_model("accounts", "UserProfile")

    UserGroup.objects.get_or_create(name=LEGACY_DEFAULT_GROUP_NAME)

    for name in DEFAULT_SIGNUP_GROUP_NAMES:
        group = UserGroup.objects.filter(name=name).first()
        if group and not UserProfile.objects.filter(group=group).exists():
            group.delete()


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0003_alter_usergroup_options_alter_userprofile_options_and_more"),
    ]

    operations = [
        migrations.RunPython(seed_signup_groups, unseed_signup_groups),
    ]
