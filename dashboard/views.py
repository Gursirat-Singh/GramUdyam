from decimal import Decimal
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import render
from accounts.views import ensure_user_profile
from business_advisor.models import BusinessPlan, BusinessRecommendation
from financial_planning.models import FinancialPlan
from market_insights.models import MarketObservation, FundingScheme
from market_insights.services import ensure_default_schemes_seeded
from reports.models import Report


def home_landing_view(request):
    '''Public home page introducing the rural business advisory platform.'''
    ensure_default_schemes_seeded()
    scheme_count = FundingScheme.objects.filter(is_active=True).count()
    return render(
        request,
        "dashboard/home.html",
        {
            "scheme_count": scheme_count,
        },
    )


@login_required
def dashboard_index_view(request):
    '''
    Personalized Entrepreneur Dashboard.
    Dynamically computes all metrics from the authenticated user's database records.
    '''
    profile = ensure_user_profile(request.user)
    ensure_default_schemes_seeded()

    user_bplans = BusinessPlan.objects.filter(user=request.user).order_by("-created_at")
    user_fplans = FinancialPlan.objects.filter(user=request.user).order_by("-updated_at")
    user_observations = MarketObservation.objects.filter(user=request.user).order_by("-observed_date")
    user_reports = Report.objects.filter(user=request.user).order_by("-generated_at")

    total_bplans = user_bplans.count()
    total_fplans = user_fplans.count()
    total_observations = user_observations.count()
    total_reports = user_reports.count()

    # Aggregated financial metrics across the user's financial plans
    fplan_list = list(user_fplans)
    if fplan_list:
        total_startup_capital = sum((p.total_startup_investment for p in fplan_list), Decimal("0.00"))
        total_monthly_revenue = sum((p.estimated_monthly_revenue for p in fplan_list), Decimal("0.00"))
        total_monthly_expenses = sum((p.total_monthly_operating_cost for p in fplan_list), Decimal("0.00"))
        total_monthly_ebitda = sum((p.estimated_monthly_ebitda for p in fplan_list), Decimal("0.00"))
        avg_profit_margin = (
            sum((p.profit_margin_percent for p in fplan_list), Decimal("0.00")) / Decimal(str(len(fplan_list)))
        ).quantize(Decimal("0.01"))
    else:
        total_startup_capital = Decimal("0.00")
        total_monthly_revenue = Decimal("0.00")
        total_monthly_expenses = Decimal("0.00")
        total_monthly_ebitda = Decimal("0.00")
        avg_profit_margin = Decimal("0.00")

    # Risk breakdown across BusinessPlans and FinancialPlans
    high_risk_count = sum(1 for p in fplan_list if p.risk_assessment == "HIGH") + sum(
        1 for b in user_bplans if b.risk_level == "HIGH"
    )
    moderate_risk_count = sum(1 for p in fplan_list if p.risk_assessment == "MODERATE") + sum(
        1 for b in user_bplans if b.risk_level == "MODERATE"
    )
    low_risk_count = sum(1 for p in fplan_list if p.risk_assessment == "LOW") + sum(
        1 for b in user_bplans if b.risk_level == "LOW"
    )

    if high_risk_count > 0:
        overall_risk_badge = "HIGH"
    elif moderate_risk_count > 0:
        overall_risk_badge = "MODERATE"
    elif low_risk_count > 0:
        overall_risk_badge = "LOW"
    else:
        overall_risk_badge = "UNASSESSED"

    # Recent recommendations across the user's business plans
    bplan_ids = [b.pk for b in user_bplans]
    recent_recommendations = (
        BusinessRecommendation.objects.filter(business_plan_id__in=bplan_ids).order_by("-created_at")[:5]
        if bplan_ids
        else []
    )

    featured_schemes = FundingScheme.objects.filter(is_active=True)[:3]

    return render(
        request,
        "dashboard/index.html",
        {
            "profile": profile,
            "total_bplans": total_bplans,
            "total_fplans": total_fplans,
            "total_observations": total_observations,
            "total_reports": total_reports,
            "total_startup_capital": total_startup_capital,
            "total_monthly_revenue": total_monthly_revenue,
            "total_monthly_expenses": total_monthly_expenses,
            "total_monthly_ebitda": total_monthly_ebitda,
            "avg_profit_margin": avg_profit_margin,
            "overall_risk_badge": overall_risk_badge,
            "high_risk_count": high_risk_count,
            "moderate_risk_count": moderate_risk_count,
            "low_risk_count": low_risk_count,
            "recent_bplans": user_bplans[:4],
            "recent_fplans": user_fplans[:4],
            "recent_recommendations": recent_recommendations,
            "recent_observations": user_observations[:4],
            "recent_reports": user_reports[:3],
            "featured_schemes": featured_schemes,
        },
    )
