from django.contrib import admin
from reports.models import Report


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "report_type", "business_plan", "financial_plan", "generated_at")
    list_filter = ("report_type",)
    search_fields = ("title", "user__username", "executive_summary")
