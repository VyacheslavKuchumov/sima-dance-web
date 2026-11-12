from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("booking", "0009_booking_is_paid_booking_is_ticket_issued")]

    operations = [
        migrations.AddField(
            model_name="event",
            name="starts_time",
            field=models.TimeField(blank=True, null=True, verbose_name="Время начала"),
        ),
    ]
