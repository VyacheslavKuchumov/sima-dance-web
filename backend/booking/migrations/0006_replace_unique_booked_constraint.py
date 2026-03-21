from django.db import migrations, models
from django.db.models import Q


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0005_alter_seat_options_seat_available_and_more'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='booking',
            name='unique_booked_seat',
        ),
        migrations.AddConstraint(
            model_name='booking',
            constraint=models.UniqueConstraint(
                condition=Q(('status', 'booked')),
                fields=('event', 'seat'),
                name='unique_booked_event_seat',
            ),
        ),
    ]
