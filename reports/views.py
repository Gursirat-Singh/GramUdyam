import json
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.text import slugify
from django.views.decorators.http import require_POST
from business_advisor.models import BusinessPlan
from financial_planning.models import FinancialPlan
from financial_planning.services import (
    calculate_financial_projections,
    build_scenario_comparisons,
    get_formula_explanations,
)
from reports.forms import ReportCreateForm
from reports.models import Report
from reports.pdf_generator import generate_report_pdf_bytes


@login_required
def report_list_view(request):
    reports_qs = Report.objects.filter(user=request.user).order_by("-generated_at")
    business_plans = BusinessPlan.objects.filter(user=request.user).order_by("-created_at")
    financial_plans = FinancialPlan.objects.filter(user=request.user).order_by("-updated_at")
    paginator = Paginator(reports_qs, 10)
    page_obj = paginator.get_page(request.GET.get("page", 1))
    return render(
        request,
        "reports/report_list.html",
        {
            "reports": page_obj.object_list,
            "page_obj": page_obj,
            "business_plans": business_plans,
            "financial_plans": financial_plans,
        },
    )


@login_required
def report_create_view(request):
    bp_id = request.GET.get("business_plan")
    fp_id = request.GET.get("financial_plan")

    if request.method == "POST":
        form = ReportCreateForm(request.POST, user=request.user)
        if form.is_valid():
            rep = form.save(commit=False)
            rep.user = request.user
            # Capture snapshot of financial scenarios and formulas
            snapshot = {"formulas": get_formula_explanations()}
            if rep.financial_plan and rep.financial_plan.user_id == request.user.pk:
                snapshot["metrics"] = calculate_financial_projections(rep.financial_plan)
                snapshot["scenarios"] = build_scenario_comparisons(rep.financial_plan)
            rep.snapshot_data = json.dumps(snapshot, default=str)
            rep.save()
            messages.success(request, f"Saved report '{rep.title}'. You can now view, print, or export it to PDF.")
            return redirect("reports:detail", pk=rep.pk)
        messages.error(request, "Please fix the errors in the report creation form.")
    else:
        initial = {}
        bp_obj = BusinessPlan.objects.filter(pk=bp_id, user=request.user).first() if bp_id and str(bp_id).isdigit() else None
        fp_obj = FinancialPlan.objects.filter(pk=fp_id, user=request.user).first() if fp_id and str(fp_id).isdigit() else None
        if not bp_obj and fp_obj and fp_obj.business_plan_id:
            bp_obj = BusinessPlan.objects.filter(pk=fp_obj.business_plan_id, user=request.user).first()
        if not fp_obj and bp_obj:
            fp_obj = bp_obj.financial_plans.filter(user=request.user).first()

        if bp_obj:
            initial["business_plan"] = bp_obj.pk
            initial["title"] = f"{bp_obj.title} — Bank & Advisory Dossier"
        if fp_obj:
            initial["financial_plan"] = fp_obj.pk
            if "title" not in initial:
                initial["title"] = f"{fp_obj.title} — Financial Structuring Report"
            initial["executive_summary"] = (
                f"Micro-enterprise financial & operational plan with total startup investment of ₹{fp_obj.total_startup_investment}, "
                f"projected monthly revenue of ₹{fp_obj.estimated_monthly_revenue}, operating profit (EBITDA) of ₹{fp_obj.estimated_monthly_ebitda} "
                f"({fp_obj.profit_margin_percent}% margin), and working capital reserve of ₹{fp_obj.working_capital_requirement}."
            )
        form = ReportCreateForm(initial=initial, user=request.user)

    return render(request, "reports/report_form.html", {"form": form})


@login_required
def report_detail_view(request, pk):
    rep = get_object_or_404(Report, pk=pk, user=request.user)
    try:
        snapshot = json.loads(rep.snapshot_data or "{}")
    except Exception:
        snapshot = {}

    scenarios = None
    metrics = None
    if rep.financial_plan:
        metrics = calculate_financial_projections(rep.financial_plan)
        scenarios = build_scenario_comparisons(rep.financial_plan)

    recommendations = []
    if rep.business_plan:
        recommendations = list(rep.business_plan.recommendations.all())

    return render(
        request,
        "reports/report_detail.html",
        {
            "report": rep,
            "metrics": metrics,
            "scenarios": scenarios,
            "recommendations": recommendations,
            "formulas": get_formula_explanations(),
            "snapshot": snapshot,
        },
    )


@login_required
def report_pdf_export_view(request, pk):
    rep = get_object_or_404(Report, pk=pk, user=request.user)
    pdf_bytes = generate_report_pdf_bytes(rep)
    filename = f"{slugify(rep.title) or 'business-report'}-{rep.pk}.pdf"
    response = HttpResponse(pdf_bytes, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


@login_required
@require_POST
def report_delete_view(request, pk):
    rep = get_object_or_404(Report, pk=pk, user=request.user)
    title = rep.title
    rep.delete()
    messages.success(request, f"Report '{title}' has been deleted.")
    return redirect("reports:list")


@login_required
def scenario_comparison_view(request):
    '''Side-by-side comparison of user's saved financial plans and their 3-scenario sensitivity.'''
    financial_plans = list(FinancialPlan.objects.filter(user=request.user).order_by("-updated_at"))
    selected_id = request.GET.get("plan_id")
    active_plan = None
    if selected_id and str(selected_id).isdigit():
        active_plan = FinancialPlan.objects.filter(pk=int(selected_id), user=request.user).first()
    if not active_plan and financial_plans:
        active_plan = financial_plans[0]

    scenarios = build_scenario_comparisons(active_plan) if active_plan else None
    return render(
        request,
        "reports/scenario_comparison.html",
        {
            "financial_plans": financial_plans,
            "active_plan": active_plan,
            "scenarios": scenarios,
        },
    )
