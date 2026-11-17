import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ("business_advisor", "0001_initial"),
        ("financial_planning", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Report",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="reports",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "business_plan",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="reports",
                        to="business_advisor.businessplan",
                    ),
                ),
                (
                    "financial_plan",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="reports",
                        to="financial_planning.financialplan",
                    ),
                ),
                ("title", models.CharField(max_length=220)),
                ("report_type", models.CharField(default="COMPREHENSIVE", max_length=40)),
                ("executive_summary", models.TextField()),
                ("snapshot_data", models.TextField(blank=True, default="{}")),
                ("generated_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
