"""Root URL configuration for Rural Business Advisor."""
from django.contrib import admin
from django.urls import include, path
from dashboard.views import home_landing_view

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home_landing_view, name="home"),
    path("accounts/", include("accounts.urls", namespace="accounts")),
    path("dashboard/", include("dashboard.urls", namespace="dashboard")),
    path("advisor/", include("business_advisor.urls", namespace="business_advisor")),
    path("finance/", include("financial_planning.urls", namespace="financial_planning")),
    path("market/", include("market_insights.urls", namespace="market_insights")),
    path("reports/", include("reports.urls", namespace="reports")),
]
