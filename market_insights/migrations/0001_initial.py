from decimal import Decimal
import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ("business_advisor", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="MarketObservation",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="market_observations",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "business_plan",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="market_observations",
                        to="business_advisor.businessplan",
                    ),
                ),
                ("state", models.CharField(max_length=100)),
                ("district", models.CharField(max_length=100)),
                ("village_or_town", models.CharField(max_length=150)),
                ("business_category", models.CharField(default="FOOD_PROCESSING", max_length=50)),
                ("observation_type", models.CharField(default="DEMAND", max_length=30)),
                ("subject_name", models.CharField(max_length=200)),
                ("observed_price_or_metric", models.CharField(blank=True, default="", max_length=120)),
                ("competitor_count", models.PositiveIntegerField(blank=True, null=True)),
                ("demand_level", models.CharField(default="MODERATE", max_length=20)),
                ("supplier_availability", models.CharField(default="BLOCK_TOWN", max_length=30)),
                ("details", models.TextField()),
                ("data_source_type", models.CharField(default="USER_PROVIDED", max_length=30)),
                ("observed_date", models.DateField(default=django.utils.timezone.localdate)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name="FundingScheme",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=250, unique=True)),
                ("short_code", models.CharField(blank=True, default="", max_length=50)),
                ("ministry_or_agency", models.CharField(max_length=200)),
                ("scheme_type", models.CharField(default="CREDIT_LINKED_SUBSIDY", max_length=40)),
                ("applicable_categories", models.CharField(default="ALL", max_length=255)),
                ("min_investment", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=12, validators=[django.core.validators.MinValueValidator(Decimal("0.00"))])),
                ("max_funding_amount", models.DecimalField(decimal_places=2, default=Decimal("1000000.00"), max_digits=12, validators=[django.core.validators.MinValueValidator(Decimal("0.00"))])),
                ("eligibility_criteria", models.TextField()),
                ("potential_benefits", models.TextField()),
                ("required_documents", models.TextField()),
                ("application_process", models.TextField()),
                ("official_source_url", models.URLField(max_length=500)),
                ("last_verification_date", models.DateField()),
                ("disclaimer_note", models.TextField()),
                ("is_active", models.BooleanField(default=True)),
            ],
        ),
    ]
