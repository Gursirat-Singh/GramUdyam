from django.contrib import admin
from financial_planning.models import FinancialPlan, FinancialExpense


@admin.register(FinancialPlan)
class FinancialPlanAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "user",
        "total_startup_investment",
        "estimated_monthly_revenue",
        "total_monthly_operating_cost",
        "estimated_monthly_ebitda",
        "profit_margin_percent",
        "risk_assessment",
    )
    list_filter = ("risk_assessment",)
    search_fields = ("title", "user__username")


@admin.register(FinancialExpense)
class FinancialExpenseAdmin(admin.ModelAdmin):
    list_display = ("financial_plan", "expense_type", "category", "description", "amount", "is_essential")
    list_filter = ("expense_type", "is_essential")
