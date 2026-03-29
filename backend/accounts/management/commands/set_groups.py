from django.core.management.base import BaseCommand

from accounts.group_defaults import DEFAULT_SIGNUP_GROUP_NAMES
from accounts.group_sync import sync_signup_groups


class Command(BaseCommand):
    help = "Create the default signup groups and clean up the unused legacy default group."

    def handle(self, *args, **options):
        result = sync_signup_groups()
        created_names = result["created_names"]
        existing_names = result["existing_names"]
        removed_legacy = result["removed_legacy"]
        legacy_name = result["legacy_name"]

        self.stdout.write(f"Signup groups ready: {len(DEFAULT_SIGNUP_GROUP_NAMES)} configured.")
        self.stdout.write(f"Created: {len(created_names)}")
        self.stdout.write(f"Already existed: {len(existing_names)}")

        if created_names:
            self.stdout.write("New groups: " + ", ".join(created_names))

        if removed_legacy:
            self.stdout.write(f"Removed unused legacy group: {legacy_name}")
        else:
            self.stdout.write(f"Legacy group kept or absent: {legacy_name}")
