from decimal import Decimal
import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="UserProfile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="profile",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                ("state", models.CharField(default="Punjab", max_length=100)),
                ("district", models.CharField(blank=True, default="", max_length=100)),
                ("village_or_town", models.CharField(blank=True, default="", max_length=150)),
                ("preferred_language", models.CharField(default="en", max_length=30)),
                ("business_interests", models.TextField(blank=True, default="")),
                ("skills", models.TextField(blank=True, default="")),
                ("available_capital", models.DecimalField(decimal_places=2, default=Decimal("50000.00"), max_digits=12, validators=[django.core.validators.MinValueValidator(Decimal("0.00"))])),
                ("phone_number", models.CharField(blank=True, default="", max_length=20)),
                ("experience_years", models.PositiveIntegerField(default=0)),
                ("shg_or_fpo_member", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
