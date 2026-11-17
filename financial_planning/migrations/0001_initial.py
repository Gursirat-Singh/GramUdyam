from decimal import Decimal
import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ("business_advisor", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="FinancialPlan",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="financial_plans",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "business_plan",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="financial_plans",
                        to="business_advisor.businessplan",
                    ),
                ),
                ("title", models.CharField(max_length=200)),
                ("available_capital", models.DecimalField(decimal_places=2, default=Decimal("50000.00"), max_digits=12)),
                ("equipment_and_setup_cost", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=12)),
                ("initial_inventory_cost", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=12)),
                ("licensing_and_contingency", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=12)),
                ("monthly_raw_material_cost", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=12)),
                ("monthly_rent_and_utilities", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=12)),
                ("monthly_salaries_and_labour", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=12)),
                ("monthly_transport_and_logistics", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=12)),
                ("monthly_marketing_expense", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=12)),
                ("monthly_other_expenses", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=12)),
                ("estimated_selling_price_per_unit", models.DecimalField(decimal_places=2, default=Decimal("100.00"), max_digits=12)),
                ("expected_monthly_sales_volume", models.DecimalField(decimal_places=2, default=Decimal("100.00"), max_digits=12)),
                ("loan_amount", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=12)),
                ("annual_interest_rate", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=5)),
                ("loan_tenure_months", models.PositiveIntegerField(default=36)),
                ("working_capital_months", models.PositiveSmallIntegerField(default=3)),
                ("total_startup_investment", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=14)),
                ("total_monthly_operating_cost", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=14)),
                ("estimated_monthly_revenue", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=14)),
                ("estimated_monthly_ebitda", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=14)),
                ("monthly_interest_cost", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=14)),
                ("monthly_loan_emi", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=14)),
                ("estimated_monthly_net_profit", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=14)),
                ("profit_margin_percent", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=7)),
                ("break_even_units", models.DecimalField(blank=True, decimal_places=2, max_digits=14, null=True)),
                ("break_even_revenue", models.DecimalField(blank=True, decimal_places=2, max_digits=14, null=True)),
                ("payback_period_months", models.DecimalField(blank=True, decimal_places=1, max_digits=8, null=True)),
                ("working_capital_requirement", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=14)),
                ("capital_gap", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=14)),
                ("risk_assessment", models.CharField(default="MODERATE", max_length=20)),
                ("notes", models.TextField(blank=True, default="")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="FinancialExpense",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "financial_plan",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="expense_items",
                        to="financial_planning.financialplan",
                    ),
                ),
                ("expense_type", models.CharField(default="FIXED_MONTHLY", max_length=25)),
                ("category", models.CharField(max_length=80)),
                ("description", models.CharField(max_length=200)),
                ("amount", models.DecimalField(decimal_places=2, max_digits=12, validators=[django.core.validators.MinValueValidator(Decimal("0.00"))])),
                ("is_essential", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
