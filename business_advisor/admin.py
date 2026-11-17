from django.contrib import admin
from business_advisor.models import BusinessPlan, BusinessRecommendation


@admin.register(BusinessPlan)
class BusinessPlanAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "business_category", "district", "investment_budget", "risk_level", "advisory_source", "created_at")
    list_filter = ("business_category", "risk_level", "advisory_source", "state")
    search_fields = ("title", "district", "village_or_town", "user__username")


@admin.register(BusinessRecommendation)
class BusinessRecommendationAdmin(admin.ModelAdmin):
    list_display = ("opportunity_name", "business_plan", "suitability_score", "estimated_startup_cost", "is_selected")
    list_filter = ("is_selected", "source_label")
