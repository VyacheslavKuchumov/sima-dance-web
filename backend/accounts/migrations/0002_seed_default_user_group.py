from django.db import migrations


def create_default_group(apps, schema_editor):
    UserGroup = apps.get_model("accounts", "UserGroup")
    UserGroup.objects.get_or_create(name="Основная группа")


def remove_default_group(apps, schema_editor):
    UserGroup = apps.get_model("accounts", "UserGroup")
    UserGroup.objects.filter(name="Основная группа").delete()


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_default_group, remove_default_group),
    ]
