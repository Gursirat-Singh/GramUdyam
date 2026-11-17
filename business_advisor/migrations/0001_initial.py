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
            name="BusinessPlan",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="business_plans",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                ("title", models.CharField(max_length=200)),
                ("business_category", models.CharField(default="FOOD_PROCESSING", max_length=50)),
                ("business_idea", models.CharField(blank=True, default="", max_length=255)),
                ("state", models.CharField(max_length=100)),
                ("district", models.CharField(max_length=100)),
                ("village_or_town", models.CharField(max_length=150)),
                ("investment_budget", models.DecimalField(decimal_places=2, max_digits=12, validators=[django.core.validators.MinValueValidator(Decimal("1000.00"))])),
                ("existing_skills", models.TextField()),
                ("existing_resources", models.TextField(blank=True, default="")),
                ("target_customers", models.CharField(max_length=255)),
                ("business_objectives", models.TextField()),
                ("constraints", models.TextField(blank=True, default="")),
                ("risk_level", models.CharField(default="MODERATE", max_length=20)),
                ("advisory_source", models.CharField(default="RULE_BASED_FALLBACK", max_length=40)),
                ("status", models.CharField(default="ACTIVE", max_length=20)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="BusinessRecommendation",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "business_plan",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="recommendations",
                        to="business_advisor.businessplan",
                    ),
                ),
                ("opportunity_name", models.CharField(max_length=200)),
                ("suitability_score", models.PositiveSmallIntegerField(default=85)),
                ("suitability_reasons", models.TextField()),
                ("initial_setup_requirements", models.TextField()),
                ("estimated_startup_cost", models.DecimalField(decimal_places=2, max_digits=12)),
                ("potential_customer_segments", models.TextField()),
                ("marketing_and_distribution", models.TextField()),
                ("major_risks", models.TextField()),
                ("mitigation_measures", models.TextField()),
                ("implementation_steps", models.TextField()),
                ("is_selected", models.BooleanField(default=False)),
                ("source_label", models.CharField(max_length=120)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
