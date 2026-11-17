from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from accounts.views import ensure_user_profile
from business_advisor.forms import BusinessAdvisoryForm
from business_advisor.models import BusinessPlan, BusinessRecommendation
from business_advisor.services import call_external_ai_provider


@login_required
def advisory_list_view(request):
    plans_qs = BusinessPlan.objects.filter(user=request.user).order_by("-created_at")
    paginator = Paginator(plans_qs, 10)
    page_obj = paginator.get_page(request.GET.get("page", 1))
    return render(
        request,
        "business_advisor/advisory_list.html",
        {
            "page_obj": page_obj,
            "plans": page_obj.object_list,
            "total_count": plans_qs.count(),
        },
    )


@login_required
def advisory_create_view(request):
    profile = ensure_user_profile(request.user)
    if request.method == "POST":
        form = BusinessAdvisoryForm(request.POST)
        if form.is_valid():
            plan = form.save(commit=False)
            plan.user = request.user
            plan_data = form.cleaned_data
            advisory_result = call_external_ai_provider(plan_data, user_id=request.user.pk)
            plan.advisory_source = advisory_result["advisory_source"]
            plan.risk_level = advisory_result["risk_level"]
            plan.save()

            for rec_data in advisory_result["recommendations"]:
                BusinessRecommendation.objects.create(
                    business_plan=plan,
                    **rec_data,
                )

            if advisory_result.get("fallback_reason"):
                messages.info(request, advisory_result["fallback_reason"])
            messages.success(
                request,
                f"Generated {len(advisory_result['recommendations'])} hyper-local business recommendations for '{plan.title}'.",
            )
            return redirect("business_advisor:detail", pk=plan.pk)
        messages.error(request, "Please fix the errors in your business advisory form.")
    else:
        initial = {
            "state": profile.state or "Punjab",
            "district": profile.district or "",
            "village_or_town": profile.village_or_town or "",
            "investment_budget": profile.available_capital,
            "existing_skills": profile.skills or "",
        }
        form = BusinessAdvisoryForm(initial=initial)

    return render(
        request,
        "business_advisor/advisory_form.html",
        {"form": form, "profile": profile},
    )


@login_required
def advisory_detail_view(request, pk):
    plan = get_object_or_404(BusinessPlan, pk=pk, user=request.user)
    recommendations = plan.recommendations.all()
    linked_financial_plans = plan.financial_plans.filter(user=request.user)
    return render(
        request,
        "business_advisor/advisory_detail.html",
        {
            "plan": plan,
            "recommendations": recommendations,
            "linked_financial_plans": linked_financial_plans,
        },
    )


@login_required
@require_POST
def advisory_select_recommendation_view(request, pk, rec_id):
    plan = get_object_or_404(BusinessPlan, pk=pk, user=request.user)
    rec = get_object_or_404(BusinessRecommendation, pk=rec_id, business_plan=plan)
    plan.recommendations.all().update(is_selected=False)
    rec.is_selected = True
    rec.save()
    messages.success(request, f"Selected '{rec.opportunity_name}' as your primary venture track.")
    return redirect("business_advisor:detail", pk=plan.pk)


@login_required
@require_POST
def advisory_delete_view(request, pk):
    plan = get_object_or_404(BusinessPlan, pk=pk, user=request.user)
    title = plan.title
    plan.delete()
    messages.success(request, f"Business plan '{title}' has been deleted.")
    return redirect("business_advisor:list")
