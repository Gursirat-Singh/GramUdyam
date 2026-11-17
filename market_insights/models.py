from decimal import Decimal
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone
from business_advisor.models import BUSINESS_CATEGORY_CHOICES, BusinessPlan


OBSERVATION_TYPE_CHOICES = [
    ("COMPETITOR", "Competitor Observation"),
    ("DEMAND", "Customer Demand & Footfall"),
    ("SUPPLIER", "Raw Material & Supplier Availability"),
    ("PRICING", "Local Retail / Mandi Price Check"),
    ("INFRASTRUCTURE", "Transport, Power & Storage Infrastructure"),
]

DEMAND_LEVEL_CHOICES = [
    ("LOW", "Low / Unproven Demand"),
    ("MODERATE", "Steady Moderate Demand"),
    ("HIGH", "High Unmet Local Demand"),
    ("SEASONAL", "Highly Seasonal (Harvest / Festival Linked)"),
]

SUPPLIER_AVAILABILITY_CHOICES = [
    ("LOCAL_VILLAGE", "Available Within Village / Gram Panchayat"),
    ("BLOCK_TOWN", "Available at Block / Tehsil Mandi (<15 km)"),
    ("DISTRICT_HQ", "Available at District Headquarters (15-50 km)"),
    ("OUTSIDE_DISTRICT", "Requires Inter-District / Wholesale Sourcing (>50 km)"),
]

DATA_SOURCE_TYPE_CHOICES = [
    ("USER_PROVIDED", "User-Recorded Field Observation"),
    ("GENERAL_GUIDANCE", "General Sector Guidance (Non-Statistical)"),
    ("ESTIMATE", "Field Estimate (Unverified)"),
]

SCHEME_TYPE_CHOICES = [
    ("CREDIT_LINKED_SUBSIDY", "Credit-Linked Capital Subsidy"),
    ("COLLATERAL_FREE_LOAN", "Collateral-Free Micro Enterprise Loan"),
    ("SHG_LIVELIHOOD", "Rural Livelihood Mission / SHG Revolving & CIF Fund"),
    ("FOOD_PROCESSING_UPGRADE", "Micro Food Processing Upgradation Scheme"),
    ("SC_ST_WOMEN_TERM_LOAN", "Inclusive Enterprise Term Loan (SC/ST/Women)"),
    ("NABARD_RURAL_INNOVATION", "NABARD Farm / Off-Farm Collectivization & Infrastructure"),
]


class MarketObservation(models.Model):
    """
    Records hyper-local field observations logged by the entrepreneur.
    Explicitly tracks data_source_type so user-recorded field notes are never
    confused with verified official statistics.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="market_observations",
    )
    business_plan = models.ForeignKey(
        BusinessPlan,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="market_observations",
    )
    state = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    village_or_town = models.CharField(max_length=150)
    business_category = models.CharField(
        max_length=50,
        choices=BUSINESS_CATEGORY_CHOICES,
        default="FOOD_PROCESSING",
    )
    observation_type = models.CharField(
        max_length=30,
        choices=OBSERVATION_TYPE_CHOICES,
        default="DEMAND",
    )
    subject_name = models.CharField(
        max_length=200,
        help_text="Name of competitor, product, mandi, or supplier observed.",
    )
    observed_price_or_metric = models.CharField(
        max_length=120,
        blank=True,
        default="",
        help_text="Observed price or volume (e.g., ₹165/litre mustard oil, 3 shops in block).",
    )
    competitor_count = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Number of existing competitors within 10 km radius (if applicable).",
    )
    demand_level = models.CharField(
        max_length=20,
        choices=DEMAND_LEVEL_CHOICES,
        default="MODERATE",
    )
    supplier_availability = models.CharField(
        max_length=30,
        choices=SUPPLIER_AVAILABILITY_CHOICES,
        default="BLOCK_TOWN",
    )
    details = models.TextField(
        help_text="Field notes on quality gaps, customer complaints, credit terms, or seasonal spikes.",
    )
    data_source_type = models.CharField(
        max_length=30,
        choices=DATA_SOURCE_TYPE_CHOICES,
        default="USER_PROVIDED",
    )
    observed_date = models.DateField(default=timezone.localdate)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-observed_date", "-created_at"]
        indexes = [
            models.Index(fields=["user", "business_category"], name="idx_mobs_user_cat"),
            models.Index(fields=["state", "district"], name="idx_mobs_location"),
        ]
        verbose_name = "Market Observation"
        verbose_name_plural = "Market Observations"

    def __str__(self):
        return f"{self.subject_name} ({self.get_observation_type_display()} - {self.village_or_town})"


class FundingScheme(models.Model):
    """
    Documented central/state government schemes for rural micro-entrepreneurs.
    Clearly distinguishes general policy guidance from confirmed individual eligibility.
    """
    name = models.CharField(max_length=250, unique=True)
    short_code = models.CharField(max_length=50, blank=True, default="")
    ministry_or_agency = models.CharField(max_length=200)
    scheme_type = models.CharField(
        max_length=40,
        choices=SCHEME_TYPE_CHOICES,
        default="CREDIT_LINKED_SUBSIDY",
    )
    applicable_categories = models.CharField(
        max_length=255,
        default="ALL",
        help_text="Comma-separated category keys or ALL.",
    )
    min_investment = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    max_funding_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("1000000.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    eligibility_criteria = models.TextField()
    potential_benefits = models.TextField()
    required_documents = models.TextField()
    application_process = models.TextField()
    official_source_url = models.URLField(max_length=500)
    last_verification_date = models.DateField()
    disclaimer_note = models.TextField(
        default=(
            "General policy guidance only based on official scheme portals. "
            "Final eligibility, subsidy sanction, and credit appraisal are determined "
            "solely by the nodal agency and lending bank. No loan approval is guaranteed."
        )
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Government Funding Scheme"
        verbose_name_plural = "Government Funding Schemes"

    def __str__(self):
        return f"{self.name} ({self.short_code})" if self.short_code else self.name
