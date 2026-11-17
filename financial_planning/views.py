from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from accounts.views import ensure_user_profile
from business_advisor.models import BusinessPlan
from financial_planning.forms import FinancialPlanForm, FinancialExpenseForm
from financial_planning.models import FinancialPlan, FinancialExpense
from financial_planning.services import (
    calculate_financial_projections,
    build_scenario_comparisons,
    get_formula_explanations,
)


@login_required
def financial_plan_list_view(request):
    plans_qs = FinancialPlan.objects.filter(user=request.user).order_by("-updated_at")
    paginator = Paginator(plans_qs, 10)
    page_obj = paginator.get_page(request.GET.get("page", 1))
    return render(
        request,
        "financial_planning/plan_list.html",
        {
            "page_obj": page_obj,
            "plans": page_obj.object_list,
            "total_count": plans_qs.count(),
        },
    )


@login_required
def financial_plan_create_view(request):
    profile = ensure_user_profile(request.user)
    linked_bplan_id = request.GET.get("business_plan")
    linked_bplan = None
    if linked_bplan_id and str(linked_bplan_id).isdigit():
        linked_bplan = BusinessPlan.objects.filter(pk=int(linked_bplan_id), user=request.user).first()

    if request.method == "POST":
        form = FinancialPlanForm(request.POST, user=request.user)
        if form.is_valid():
            fplan = form.save(commit=False)
            fplan.user = request.user
            fplan.save()
            messages.success(
                request,
                f"Financial plan '{fplan.title}' calculated and saved.",
            )
            return redirect("financial_planning:detail", pk=fplan.pk)
        messages.error(request, "Please correct the highlighted errors in the financial planning form.")
    else:
        initial = {
            "available_capital": profile.available_capital,
            "loan_tenure_months": 36,
            "working_capital_months": 3,
            "annual_interest_rate": Decimal("9.50"),
        }
        if linked_bplan:
            initial["business_plan"] = linked_bplan.pk
            initial["title"] = f"{linked_bplan.title} — Financial Model"
            selected_rec = linked_bplan.recommendations.filter(is_selected=True).first() or linked_bplan.recommendations.first()
            if selected_rec:
                est_startup = selected_rec.estimated_startup_cost
                initial["equipment_and_setup_cost"] = (est_startup * Decimal("0.65")).quantize(Decimal("0.01"))
                initial["initial_inventory_cost"] = (est_startup * Decimal("0.25")).quantize(Decimal("0.01"))
                initial["licensing_and_contingency"] = (est_startup * Decimal("0.10")).quantize(Decimal("0.01"))
        form = FinancialPlanForm(initial=initial, user=request.user)

    return render(
        request,
        "financial_planning/plan_form.html",
        {
            "form": form,
            "is_edit": False,
            "formulas": get_formula_explanations(),
        },
    )


@login_required
def financial_plan_detail_view(request, pk):
    fplan = get_object_or_404(FinancialPlan, pk=pk, user=request.user)
    metrics = calculate_financial_projections(fplan)
    scenarios = build_scenario_comparisons(fplan)
    formulas = get_formula_explanations()
    expense_items = fplan.expense_items.all()
    expense_form = FinancialExpenseForm()

    # Build CSS percentage bar ratios for visual chart
    max_val = max(
        Decimal("1.00"),
        metrics["estimated_monthly_revenue"],
        metrics["total_monthly_operating_cost"],
        abs(metrics["estimated_monthly_ebitda"]),
    )
    chart_bars = {
        "revenue_pct": int(min(100, (metrics["estimated_monthly_revenue"] / max_val) * 100)),
        "opex_pct": int(min(100, (metrics["total_monthly_operating_cost"] / max_val) * 100)),
        "ebitda_pct": int(min(100, (max(Decimal("0.00"), metrics["estimated_monthly_ebitda"]) / max_val) * 100)),
    }

    return render(
        request,
        "financial_planning/plan_detail.html",
        {
            "plan": fplan,
            "metrics": metrics,
            "scenarios": scenarios,
            "formulas": formulas,
            "expense_items": expense_items,
            "expense_form": expense_form,
            "chart_bars": chart_bars,
        },
    )


@login_required
def financial_plan_edit_view(request, pk):
    fplan = get_object_or_404(FinancialPlan, pk=pk, user=request.user)
    if request.method == "POST":
        form = FinancialPlanForm(request.POST, instance=fplan, user=request.user)
        if form.is_valid():
            updated = form.save(commit=False)
            updated.user = request.user
            updated.save()
            messages.success(request, f"Assumptions updated and projections recalculated for '{updated.title}'.")
            return redirect("financial_planning:detail", pk=updated.pk)
        messages.error(request, "Please review the form for invalid financial inputs.")
    else:
        form = FinancialPlanForm(instance=fplan, user=request.user)

    return render(
        request,
        "financial_planning/plan_form.html",
        {
            "form": form,
            "plan": fplan,
            "is_edit": True,
            "formulas": get_formula_explanations(),
        },
    )


@login_required
@require_POST
def financial_plan_delete_view(request, pk):
    fplan = get_object_or_404(FinancialPlan, pk=pk, user=request.user)
    title = fplan.title
    fplan.delete()
    messages.success(request, f"Financial plan '{title}' has been deleted.")
    return redirect("financial_planning:list")


@login_required
@require_POST
def financial_expense_add_view(request, pk):
    fplan = get_object_or_404(FinancialPlan, pk=pk, user=request.user)
    form = FinancialExpenseForm(request.POST)
    if form.is_valid():
        item = form.save(commit=False)
        item.financial_plan = fplan
        item.save()
        messages.success(request, f"Added expense item '{item.description}' (₹{item.amount}).")
    else:
        messages.error(request, "Could not add expense item. Ensure description and positive amount are provided.")
    return redirect("financial_planning:detail", pk=fplan.pk)


@login_required
@require_POST
def financial_expense_delete_view(request, pk, expense_id):
    fplan = get_object_or_404(FinancialPlan, pk=pk, user=request.user)
    item = get_object_or_404(FinancialExpense, pk=expense_id, financial_plan=fplan)
    item.delete()
    messages.success(request, "Expense line item removed.")
    return redirect("financial_planning:detail", pk=fplan.pk)
