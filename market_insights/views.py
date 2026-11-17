from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from accounts.views import ensure_user_profile
from business_advisor.models import BUSINESS_CATEGORY_CHOICES
from market_insights.forms import MarketObservationForm
from market_insights.models import MarketObservation, FundingScheme
from market_insights.services import (
    ensure_default_schemes_seeded,
    get_regional_category_guidance,
    build_regional_market_synthesis,
)


@login_required
def market_overview_view(request):
    profile = ensure_user_profile(request.user)
    selected_category = request.GET.get("category", "")
    obs_qs = MarketObservation.objects.filter(user=request.user).order_by("-observed_date", "-created_at")
    if selected_category:
        obs_qs = obs_qs.filter(business_category=selected_category)

    synthesis = build_regional_market_synthesis(obs_qs, selected_category or "FOOD_PROCESSING")
    guidance = get_regional_category_guidance(selected_category or "FOOD_PROCESSING")

    paginator = Paginator(obs_qs, 10)
    page_obj = paginator.get_page(request.GET.get("page", 1))

    initial_form_data = {
        "state": profile.state or "Punjab",
        "district": profile.district or "",
        "village_or_town": profile.village_or_town or "",
        "business_category": selected_category or "FOOD_PROCESSING",
    }
    form = MarketObservationForm(initial=initial_form_data, user=request.user)

    return render(
        request,
        "market_insights/market_overview.html",
        {
            "profile": profile,
            "categories": BUSINESS_CATEGORY_CHOICES,
            "selected_category": selected_category,
            "observations": page_obj.object_list,
            "page_obj": page_obj,
            "synthesis": synthesis,
            "guidance": guidance,
            "form": form,
        },
    )


@login_required
def observation_create_view(request):
    profile = ensure_user_profile(request.user)
    if request.method == "POST":
        form = MarketObservationForm(request.POST, user=request.user)
        if form.is_valid():
            obs = form.save(commit=False)
            obs.user = request.user
            obs.data_source_type = "USER_PROVIDED"
            obs.save()
            messages.success(
                request,
                f"Recorded hyper-local observation '{obs.subject_name}' (labelled as User-Recorded Field Data).",
            )
            return redirect("market_insights:overview")
        messages.error(request, "Please fix the errors in your market observation form.")
    else:
        form = MarketObservationForm(
            initial={
                "state": profile.state or "Punjab",
                "district": profile.district or "",
                "village_or_town": profile.village_or_town or "",
            },
            user=request.user,
        )
    return render(request, "market_insights/observation_form.html", {"form": form})


@login_required
@require_POST
def observation_delete_view(request, pk):
    obs = get_object_or_404(MarketObservation, pk=pk, user=request.user)
    subj = obs.subject_name
    obs.delete()
    messages.success(request, f"Removed market observation '{subj}'.")
    return redirect("market_insights:overview")


@login_required
def funding_schemes_list_view(request):
    ensure_default_schemes_seeded()
    category_filter = request.GET.get("category", "")
    schemes_qs = FundingScheme.objects.filter(is_active=True)
    schemes = list(schemes_qs)
    if category_filter:
        schemes = [
            s for s in schemes
            if s.applicable_categories == "ALL" or category_filter in s.applicable_categories.split(",")
        ]

    return render(
        request,
        "market_insights/schemes_list.html",
        {
            "schemes": schemes,
            "categories": BUSINESS_CATEGORY_CHOICES,
            "selected_category": category_filter,
        },
    )


@login_required
def funding_scheme_detail_view(request, pk):
    ensure_default_schemes_seeded()
    scheme = get_object_or_404(FundingScheme, pk=pk)
    return render(request, "market_insights/scheme_detail.html", {"scheme": scheme})
