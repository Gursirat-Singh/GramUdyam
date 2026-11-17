from decimal import Decimal
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


BUSINESS_CATEGORY_CHOICES = [
    ("AGRI_ALLIED", "Agriculture & Allied Services (Custom Hiring, Seed/Input Unit, Nursery)"),
    ("FOOD_PROCESSING", "Food Processing & Value Addition (Flour/Oil Mill, Pickles, Millet Snacks, Spices)"),
    ("DAIRY_LIVESTOCK", "Dairy, Poultry & Livestock (Milk Chilling, Paneer/Ghee Unit, Goat/Poultry Feed)"),
    ("RURAL_RETAIL", "Rural Retail, Kirana & CSC Digital Commerce"),
    ("HANDICRAFTS_TEXTILE", "Handicrafts, Handloom, Tailoring & Apparel"),
    ("RURAL_SERVICES", "Rural Repair, Two-Wheeler/Tractor Servicing & Logistics"),
    ("RENEWABLE_AGRITECH", "Solar Cold Storage, Biomass Briquettes & Agri-Tech Services"),
    ("SMALL_MANUFACTURING", "Eco-Friendly Packaging, Paper Plates, Detergent & Bricks"),
]

RISK_LEVEL_CHOICES = [
    ("LOW", "Low Risk"),
    ("MODERATE", "Moderate Risk"),
    ("HIGH", "High Risk"),
]

PLAN_STATUS_CHOICES = [
    ("DRAFT", "Draft"),
    ("ACTIVE", "Active"),
    ("ARCHIVED", "Archived"),
]

ADVISORY_SOURCE_CHOICES = [
    ("RULE_BASED_FALLBACK", "Rule-Based Domain Engine (Offline Fallback - Verified Templates)"),
    ("AI_PROVIDER", "External AI Provider (LLM Assisted)"),
]


class BusinessPlan(models.Model):
    """Represents a rural entrepreneur's business advisory profile and venture blueprint."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="business_plans",
    )
    title = models.CharField(
        max_length=200,
        help_text="Descriptive title for your business plan (e.g., Village Mini Oil Expeller & Mustard Cake Unit).",
    )
    business_category = models.CharField(
        max_length=50,
        choices=BUSINESS_CATEGORY_CHOICES,
        default="FOOD_PROCESSING",
    )
    business_idea = models.CharField(
        max_length=255,
        blank=True,
        default="",
        help_text="Specific business idea if you already have one in mind (optional).",
    )
    state = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    village_or_town = models.CharField(max_length=150)
    investment_budget = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("1000.00"))],
        help_text="Total capital budget available (own savings + potential loan in INR ₹).",
    )
    existing_skills = models.TextField(
        help_text="Skills available within your household or team.",
    )
    existing_resources = models.TextField(
        blank=True,
        default="",
        help_text="Existing land, shed, electricity connection, vehicle, or farm produce.",
    )
    target_customers = models.CharField(
        max_length=255,
        help_text="Who will buy your product/service? (e.g., village households, local mandis, block retailers).",
    )
    business_objectives = models.TextField(
        help_text="Income goals, employment generation, or seasonal diversification targets.",
    )
    constraints = models.TextField(
        blank=True,
        default="",
        help_text="Local challenges (e.g., power cuts, seasonal road access, limited cold chain).",
    )
    risk_level = models.CharField(
        max_length=20,
        choices=RISK_LEVEL_CHOICES,
        default="MODERATE",
    )
    advisory_source = models.CharField(
        max_length=40,
        choices=ADVISORY_SOURCE_CHOICES,
        default="RULE_BASED_FALLBACK",
    )
    status = models.CharField(
        max_length=20,
        choices=PLAN_STATUS_CHOICES,
        default="ACTIVE",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "-created_at"], name="idx_bplan_user_date"),
            models.Index(fields=["business_category"], name="idx_bplan_category"),
        ]
        verbose_name = "Business Plan"
        verbose_name_plural = "Business Plans"

    def __str__(self):
        return f"{self.title} ({self.village_or_town}, {self.district})"


class BusinessRecommendation(models.Model):
    """Structured business opportunity recommendation linked to a BusinessPlan."""
    business_plan = models.ForeignKey(
        BusinessPlan,
        on_delete=models.CASCADE,
        related_name="recommendations",
    )
    opportunity_name = models.CharField(max_length=200)
    suitability_score = models.PositiveSmallIntegerField(
        default=85,
        validators=[MinValueValidator(1), MaxValueValidator(100)],
    )
    suitability_reasons = models.TextField()
    initial_setup_requirements = models.TextField()
    estimated_startup_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    potential_customer_segments = models.TextField()
    marketing_and_distribution = models.TextField()
    major_risks = models.TextField()
    mitigation_measures = models.TextField()
    implementation_steps = models.TextField()
    is_selected = models.BooleanField(default=False)
    source_label = models.CharField(
        max_length=120,
        default="Rule-Based Hyper-Local Advisory Fallback (Verified Sector Heuristics)",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-suitability_score", "id"]
        verbose_name = "Business Recommendation"
        verbose_name_plural = "Business Recommendations"

    def __str__(self):
        return f"{self.opportunity_name} ({self.suitability_score}% match)"
