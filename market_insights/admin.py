from django.contrib import admin
from market_insights.models import MarketObservation, FundingScheme


@admin.register(MarketObservation)
class MarketObservationAdmin(admin.ModelAdmin):
    list_display = ("subject_name", "user", "observation_type", "business_category", "village_or_town", "district", "demand_level", "data_source_type")
    list_filter = ("observation_type", "business_category", "demand_level", "data_source_type", "state")
    search_fields = ("subject_name", "village_or_town", "district", "details")


@admin.register(FundingScheme)
class FundingSchemeAdmin(admin.ModelAdmin):
    list_display = ("name", "short_code", "ministry_or_agency", "scheme_type", "max_funding_amount", "last_verification_date", "is_active")
    list_filter = ("scheme_type", "is_active")
    search_fields = ("name", "short_code", "ministry_or_agency")
