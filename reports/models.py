from django.contrib.auth.models import User
from django.db import models
from business_advisor.models import BusinessPlan
from financial_planning.models import FinancialPlan


REPORT_TYPE_CHOICES = [
    ("COMPREHENSIVE", "Comprehensive Business & Financial Structuring Dossier"),
    ("FINANCIAL_SUMMARY", "Financial Projections, Break-Even & 3-Scenario Report"),
    ("ADVISORY_BRIEF", "Hyper-Local Opportunity & Risk Mitigation Brief"),
    ("BANK_LOAN_PROPOSAL", "Micro-Enterprise Bank / MUDRA / PMEGP Appraisal Summary"),
]


class Report(models.Model):
    """
    Saved, print-ready and PDF-exportable report combining a user's BusinessPlan,
    FinancialPlan, MarketObservations, and relevant FundingSchemes.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="reports",
    )
    title = models.CharField(max_length=220)
    business_plan = models.ForeignKey(
        BusinessPlan,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reports",
    )
    financial_plan = models.ForeignKey(
        FinancialPlan,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reports",
    )
    report_type = models.CharField(
        max_length=40,
        choices=REPORT_TYPE_CHOICES,
        default="COMPREHENSIVE",
    )
    executive_summary = models.TextField()
    snapshot_data = models.TextField(
        blank=True,
        default="{}",
        help_text="JSON snapshot of calculated metrics, formulas, and assumptions at report creation.",
    )
    generated_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-generated_at"]
        indexes = [
            models.Index(fields=["user", "-generated_at"], name="idx_report_user_date"),
        ]
        verbose_name = "Saved Report"
        verbose_name_plural = "Saved Reports"

    def __str__(self):
        return f"{self.title} ({self.get_report_type_display()})"
