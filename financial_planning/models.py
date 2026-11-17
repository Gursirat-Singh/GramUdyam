from decimal import Decimal
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from business_advisor.models import BusinessPlan


EXPENSE_TYPE_CHOICES = [
    ("STARTUP", "One-Time Startup Capital Expense"),
    ("FIXED_MONTHLY", "Fixed Monthly Operating Expense"),
    ("VARIABLE_MONTHLY", "Variable Monthly Operating Expense"),
]


class FinancialPlan(models.Model):
    """
    Stores both user-entered financial assumptions and Decimal-computed projections
    for a rural micro-enterprise.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="financial_plans",
    )
    business_plan = models.ForeignKey(
        BusinessPlan,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="financial_plans",
        help_text="Optional linked Business Plan.",
    )
    title = models.CharField(
        max_length=200,
        help_text="Title for this financial model (e.g., Mustard Oil Mill - Base Plan).",
    )

    # --- USER-ENTERED ASSUMPTIONS ---
    available_capital = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("50000.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
        help_text="Own savings / promoter contribution available (₹).",
    )
    equipment_and_setup_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
        help_text="Machinery, tools, shed modification, and installation costs (₹).",
    )
    initial_inventory_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
        help_text="Initial raw material stock, packaging, and opening inventory (₹).",
    )
    licensing_and_contingency = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
        help_text="FSSAI/Udyam registration, security deposit, and startup contingency (₹).",
    )

    # Monthly Operating Expense Assumptions
    monthly_raw_material_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
        help_text="Monthly raw materials, inputs, or stock replenishment cost (₹/month).",
    )
    monthly_rent_and_utilities = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
        help_text="Shop/shed rent, electricity, water, fuel, and internet (₹/month).",
    )
    monthly_salaries_and_labour = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
        help_text="Helper wages, operator salary, and daily labour charges (₹/month).",
    )
    monthly_transport_and_logistics = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
        help_text="Mandi transport, local delivery, and freight expenses (₹/month).",
    )
    monthly_marketing_expense = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
        help_text="Signboards, local haat promotion, banners, and packaging labels (₹/month).",
    )
    monthly_other_expenses = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
        help_text="Maintenance, repairs, accounting, and miscellaneous recurring costs (₹/month).",
    )

    # Revenue Assumptions
    estimated_selling_price_per_unit = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("100.00"),
        validators=[MinValueValidator(Decimal("0.01"))],
        help_text="Average selling price per unit / kg / litre / service job (₹).",
    )
    expected_monthly_sales_volume = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("100.00"),
        validators=[MinValueValidator(Decimal("0.01"))],
        help_text="Expected number of units / kg / litres / jobs sold per month.",
    )

    # Financing & Working Capital Assumptions
    loan_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
        help_text="Term loan or MUDRA / SHG loan amount required (₹).",
    )
    annual_interest_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00")), MaxValueValidator(Decimal("60.00"))],
        help_text="Annual loan interest rate in % (e.g., 9.50 for 9.5% p.a.).",
    )
    loan_tenure_months = models.PositiveIntegerField(
        default=36,
        validators=[MinValueValidator(1), MaxValueValidator(240)],
        help_text="Loan repayment period in months (e.g., 36 months = 3 years).",
    )
    working_capital_months = models.PositiveSmallIntegerField(
        default=3,
        validators=[MinValueValidator(1), MaxValueValidator(24)],
        help_text="Number of months of operating expenses to buffer as working capital (typically 2-4 months).",
    )

    # --- CALCULATED ESTIMATES (Computed by Decimal Engine) ---
    total_startup_investment = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    total_monthly_operating_cost = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    estimated_monthly_revenue = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    estimated_monthly_ebitda = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Estimated monthly profit before taxes and financing costs.",
    )
    monthly_interest_cost = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    monthly_loan_emi = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    estimated_monthly_net_profit = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Estimated monthly profit after monthly loan interest cost.",
    )
    profit_margin_percent = models.DecimalField(max_digits=7, decimal_places=2, default=Decimal("0.00"))
    break_even_units = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    break_even_revenue = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    payback_period_months = models.DecimalField(max_digits=8, decimal_places=1, null=True, blank=True)
    working_capital_requirement = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    capital_gap = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    risk_assessment = models.CharField(max_length=20, default="MODERATE")

    notes = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
        indexes = [
            models.Index(fields=["user", "-updated_at"], name="idx_fplan_user_date"),
        ]
        verbose_name = "Financial Plan"
        verbose_name_plural = "Financial Plans"

    def recalculate_and_apply(self):
        """Runs the Decimal financial calculation engine and updates computed fields."""
        from financial_planning.services import calculate_financial_projections
        metrics = calculate_financial_projections(self)
        self.total_startup_investment = metrics["total_startup_investment"]
        self.total_monthly_operating_cost = metrics["total_monthly_operating_cost"]
        self.estimated_monthly_revenue = metrics["estimated_monthly_revenue"]
        self.estimated_monthly_ebitda = metrics["estimated_monthly_ebitda"]
        self.monthly_interest_cost = metrics["monthly_interest_cost"]
        self.monthly_loan_emi = metrics["monthly_loan_emi"]
        self.estimated_monthly_net_profit = metrics["estimated_monthly_net_profit"]
        self.profit_margin_percent = metrics["profit_margin_percent"]
        self.break_even_units = metrics["break_even_units"]
        self.break_even_revenue = metrics["break_even_revenue"]
        self.payback_period_months = metrics["payback_period_months"]
        self.working_capital_requirement = metrics["working_capital_requirement"]
        self.capital_gap = metrics["capital_gap"]
        self.risk_assessment = metrics["risk_assessment"]
        return metrics

    def save(self, *args, **kwargs):
        self.recalculate_and_apply()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} (Rev: ₹{self.estimated_monthly_revenue}/mo)"


class FinancialExpense(models.Model):
    """Granular expense line item linked to a FinancialPlan."""
    financial_plan = models.ForeignKey(
        FinancialPlan,
        on_delete=models.CASCADE,
        related_name="expense_items",
    )
    expense_type = models.CharField(
        max_length=25,
        choices=EXPENSE_TYPE_CHOICES,
        default="FIXED_MONTHLY",
    )
    category = models.CharField(max_length=80)
    description = models.CharField(max_length=200)
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    is_essential = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["expense_type", "-amount"]
        verbose_name = "Financial Expense Line Item"
        verbose_name_plural = "Financial Expense Line Items"

    def __str__(self):
        return f"{self.category}: {self.description} (₹{self.amount})"
