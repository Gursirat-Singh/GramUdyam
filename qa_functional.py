"""
Temporary comprehensive QA functional audit script for GramVenture AI.
AUDIT-ONLY: no changes to existing source; uses an isolated in-memory test DB.
"""
import os
import time
import json
from decimal import Decimal, ROUND_HALF_UP

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django

django.setup()

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse, NoReverseMatch
from django.db import connection

from financial_planning.services import (
    calculate_financial_projections,
    calculate_loan_schedule,
    build_scenario_comparisons,
)
from business_advisor.services import (
    generate_rule_based_recommendations,
    call_external_ai_provider,
    check_and_increment_ai_rate_limit,
)
from market_insights.services import ensure_default_schemes_seeded
from market_insights.models import FundingScheme, MarketObservation
from business_advisor.models import BusinessPlan, BusinessRecommendation
from financial_planning.models import FinancialPlan
from reports.models import Report
from accounts.models import UserProfile

ZERO = Decimal("0.00")

RESULTS = {"pass": 0, "fail": 0, "partial": 0, "not_tested": 0, "cases": []}


def record(test_id, module, scenario, precond, steps, expected, actual, status, severity, evidence):
    RESULTS["cases"].append(
        {
            "test_id": test_id,
            "module": module,
            "scenario": scenario,
            "preconditions": precond,
            "steps": steps,
            "expected": expected,
            "actual": actual,
            "status": status,
            "severity": severity,
            "evidence": evidence,
        }
    )
    if status == "PASS":
        RESULTS["pass"] += 1
    elif status == "FAIL":
        RESULTS["fail"] += 1
    elif status == "PARTIAL":
        RESULTS["partial"] += 1
    else:
        RESULTS["not_tested"] += 1
    print(f"[{status}] {test_id} - {scenario}")


def money(d):
    return Decimal(str(d)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


    # ---------------------------------------------------------------- URL MATRIX
    def test_url_status_matrix(self):
        """Every registered URL returns the expected HTTP status (anonymous + authenticated)."""
        public_urls = [("home", {}, False)]
        protected_urls = [
            ("accounts:profile", {}, True),
            ("accounts:password_reset", {}, True),
            ("accounts:password_reset_done", {}, True),
            ("accounts:logout", {}, True),
            ("dashboard:index", {}, True),
            ("business_advisor:list", {}, True),
            ("business_advisor:create", {}, True),
            ("business_advisor:detail", {"pk": 99999}, True),
            ("business_advisor:delete", {"pk": 99999}, True),
            ("business_advisor:select_recommendation", {"pk": 1, "rec_id": 1}, True),
            ("financial_planning:list", {}, True),
            ("financial_planning:create", {}, True),
            ("financial_planning:detail", {"pk": 99999}, True),
            ("financial_planning:edit", {"pk": 99999}, True),
            ("financial_planning:delete", {"pk": 99999}, True),
            ("financial_planning:add_expense", {"pk": 99999}, True),
            ("financial_planning:delete_expense", {"pk": 1, "expense_id": 1}, True),
            ("market_insights:overview", {}, True),
            ("market_insights:add_observation", {}, True),
            ("market_insights:delete_observation", {"pk": 99999}, True),
            ("market_insights:schemes_list", {}, True),
            ("market_insights:scheme_detail", {"pk": 1}, True),
            ("reports:list", {}, True),
            ("reports:create", {}, True),
            ("reports:compare", {}, True),
            ("reports:detail", {"pk": 99999}, True),
            ("reports:export_pdf", {"pk": 99999}, True),
            ("reports:delete", {"pk": 99999}, True),
        ]

        anon = Client(enforce_csrf_checks=True)
        failures = []
        for name, kwargs, protected in public_urls + protected_urls:
            try:
                url = reverse(name, kwargs=kwargs)
            except NoReverseMatch as exc:
                failures.append(f"{name}: NoReverseMatch {exc}")
                continue
            resp = anon.get(url)
            if protected:
                if resp.status_code != 302 or "/accounts/login/" not in resp.headers.get("Location", ""):
                    failures.append(
                        f"{name} ({url}): anonymous expected 302 to login, got {resp.status_code}"
                    )
            else:
                if resp.status_code != 200:
                    failures.append(f"{name} ({url}): public expected 200, got {resp.status_code}")

        for name, kwargs, protected in protected_urls:
            try:
                url = reverse(name, kwargs=kwargs)
            except NoReverseMatch as exc:
                failures.append(f"{name}: NoReverseMatch {exc}")
                continue
            resp = self.client.get(url)
            if kwargs.get("pk") == 99999:
                if resp.status_code != 404:
                    failures.append(f"{name} ({url}): owner, nonexistent pk expected 404, got {resp.status_code}")
            else:
                if resp.status_code not in (200, 302):
                    failures.append(
        # Cross-user IDOR: u2 tries to access u1's resources
        plan = BusinessPlan.objects.create(
            user=self.u1,
            title="IDOR Target Plan",
            business_category="FOOD_PROCESSING",
            state="Punjab",
            district="Ludhiana",
            village_or_town="Samrala",
            investment_budget=Decimal("75000.00"),
            existing_skills="Tailoring",
            target_customers="Local households",
            business_objectives="Income",
        )
        BusinessRecommendation.objects.create(
            business_plan=plan,
            opportunity_name="Test Opp",
            suitability_score=85,
            suitability_reasons="r",
            initial_setup_requirements="r",
            estimated_startup_cost=Decimal("10000.00"),
            potential_customer_segments="r",
            marketing_and_distribution="r",
            major_risks="r",
            mitigation_measures="r",
            implementation_steps="r",
        )
        fplan = FinancialPlan.objects.create(
            user=self.u1,
            title="IDOR Target Financial Plan",
            available_capital=Decimal("50000.00"),
            estimated_selling_price_per_unit=Decimal("100.00"),
            expected_monthly_sales_volume=Decimal("100.00"),
        )
        rep = Report.objects.create(
            user=self.u1,
            title="IDOR Target Report",
            report_type="COMPREHENSIVE",
            executive_summary="summary",
            financial_plan=fplan,
        )
        self.client.logout()
        self.client.login(username="entrepreneur_b", password="SecurePass@2026")
        idor_checks = [
            ("business_advisor:detail", {"pk": plan.pk}),
            ("business_advisor:delete", {"pk": plan.pk}),
            ("business_advisor:select_recommendation", {"pk": plan.pk, "rec_id": 1}),
            ("financial_planning:detail", {"pk": fplan.pk}),
            ("financial_planning:edit", {"pk": fplan.pk}),
            ("financial_planning:delete", {"pk": fplan.pk}),
            ("reports:detail", {"pk": rep.pk}),
            ("reports:export_pdf", {"pk": rep.pk}),
            ("reports:delete", {"pk": rep.pk}),
        ]
        for name, kwargs in idor_checks:
            resp = self.client.get(reverse(name, kwargs=kwargs))
            if resp.status_code != 404:
                failures.append(f"IDOR {name} pk={kwargs['pk']}: u2 got {resp.status_code}, expected 404")

        evidence = "\n".join(failures) if failures else "All URL status-code expectations met"
        record(
            "QA-FUNC-001",
            "Routing / Navigation",
            "URL status matrix: anonymous redirect, authenticated access, 404 on missing, IDOR blocked",
            "Fresh test DB; two users created; u1 owns sample plan/financial plan/report",
            "GET every registered URL with anonymous and authenticated clients; cross-user GET on u1's resources as u2",
            "Protected URLs redirect anonymous to login; authenticated owners get 200; nonexistent pk -> 404; cross-user access -> 404",
            "PASS" if not failures else "FAIL",
            "CRITICAL" if failures else "LOW",
            evidence,
    # ---------------------------------------------------------------- AUTH
    def test_auth_flows(self):
        """Registration, login, logout, duplicate handling, protected-page access."""
        c = Client(enforce_csrf_checks=True)
        reg_data = {
            "username": "new_user",
            "first_name": "New",
            "last_name": "User",
            "email": "new@example.com",
            "state": "Punjab",
            "district": "Ludhiana",
            "village_or_town": "Samrala",
            "preferred_language": "en",
            "available_capital": "50000.00",
            "skills": "Weaving",
            "business_interests": "Handicrafts",
            "password1": "StrongPass@2026",
            "password2": "StrongPass@2026",
        }
        resp = c.post(reverse("accounts:register"), data=reg_data, follow=True)
        reg_ok = resp.status_code == 200 and User.objects.filter(username="new_user").exists()
        profile_ok = UserProfile.objects.filter(user__username="new_user").exists()

        resp_dup = c.post(reverse("accounts:register"), data=reg_data)
        dup_ok = resp_dup.status_code == 200 and "form" in resp_dup.context

        bad = dict(reg_data)
        bad["username"] = "new_user2"
        bad["email"] = "not-an-email"
        resp_bad = c.post(reverse("accounts:register"), data=bad)
        bad_email_ok = resp_bad.status_code == 200 and "email" in resp_bad.context["form"].errors

        resp_login = c.post(reverse("accounts:login"), data={"username": "new_user", "password": "StrongPass@2026"})
        login_ok = resp_login.status_code == 302 and c.session.get("_auth_user_id") is not None

        resp_bad_login = c.post(reverse("accounts:login"), data={"username": "new_user", "password": "WrongPass"})
        bad_login_ok = resp_bad_login.status_code == 200

        resp_logout = c.get(reverse("accounts:logout"))
        logout_ok = resp_logout.status_code == 302 and c.session.get("_auth_user_id") is None

        c.logout()
        resp_prot = c.get(reverse("dashboard:index"))
        prot_ok = resp_prot.status_code == 302

        failures = []
        for label, ok in [
            ("registration", reg_ok), ("profile created", profile_ok),
            ("duplicate username rejected", dup_ok), ("invalid email rejected", bad_email_ok),
            ("valid login", login_ok), ("invalid login rejected", bad_login_ok),
            ("logout", logout_ok), ("protected redirects anonymous", prot_ok),
        ]:
            if not ok:
                failures.append(label)

        record(
            "QA-FUNC-002",
            "Authentication",
    # ---------------------------------------------------------------- ADVISORY
    def test_advisory_module(self):
        """Business advisory form, rule-based fallback, persistence, AI failure fallback."""
        plan_data = {
            "business_category": "FOOD_PROCESSING",
            "investment_budget": Decimal("90000.00"),
            "state": "Punjab",
            "district": "Ludhiana",
            "village_or_town": "Samrala",
            "existing_skills": "Tailoring and embroidery",
            "existing_resources": "Room with power",
            "target_customers": "Village households",
            "business_objectives": "Earn ₹20,000/month",
            "constraints": "Power cuts",
        }
        res = generate_rule_based_recommendations(plan_data)
        rb_ok = (
            res["advisory_source"] == "RULE_BASED_FALLBACK"
            and len(res["recommendations"]) >= 2
            and all("Rule-Based" in r["source_label"] for r in res["recommendations"])
            and all(r["estimated_startup_cost"] > 0 for r in res["recommendations"])
        )

        res_ai = call_external_ai_provider(plan_data, user_id=self.u1.pk)
        ai_ok = res_ai["advisory_source"] == "RULE_BASED_FALLBACK" and len(res_ai["recommendations"]) >= 2

        from django.core.cache import cache
        cache.clear()
        allowed, remaining = check_and_increment_ai_rate_limit(self.u1.pk)
        rate_ok = allowed is True

        post_data = {
            "title": "Samrala Spice Unit",
            "state": "Punjab",
            "district": "Ludhiana",
            "village_or_town": "Samrala",
            "investment_budget": "75000.00",
            "business_category": "FOOD_PROCESSING",
            "business_idea": "Turmeric chilli powder",
            "existing_skills": "Spice drying",
            "existing_resources": "150 sq ft room",
            "target_customers": "Village households",
            "business_objectives": "Earn ₹18,000/month",
            "constraints": "Monsoon humidity",
        }
        resp = self.client.post(reverse("business_advisor:create"), data=post_data, follow=True)
        view_ok = resp.status_code == 200
        plan_qs = BusinessPlan.objects.filter(user=self.u1)
        persisted = plan_qs.exists()
        recs_count = plan_qs.first().recommendations.count() if persisted else 0

        bad = dict(post_data)
        bad["investment_budget"] = "500.00"
        resp_bad = self.client.post(reverse("business_advisor:create"), data=bad)
        invalid_ok = resp_bad.status_code == 200 and "investment_budget" in resp_bad.context["form"].errors

        detail_ok = False
        if persisted:
            resp_detail = self.client.get(reverse("business_advisor:detail", kwargs={"pk": plan_qs.first().pk}))
            detail_ok = resp_detail.status_code == 200

        failures = []
        for label, ok in [
            ("rule-based fallback", rb_ok), ("AI-off fallback", ai_ok), ("rate limit", rate_ok),
            ("view create", view_ok), ("persistence", persisted), ("recommendations persisted", recs_count >= 2),
            ("invalid budget rejected", invalid_ok), ("detail view", detail_ok),
        ]:
            if not ok:
                failures.append(label)

        core_ok = rb_ok and ai_ok and persisted
        record(
            "QA-FUNC-003",
            "AI Business Advisory",
            "Rule-based fallback, AI disabled fallback, rate limiting, form validation, persistence, detail view",
    # ---------------------------------------------------------------- FINANCIAL
    def test_financial_calculations(self):
        """Independent verification of every financial metric plus edge cases."""
        def proj(inputs):
            return calculate_financial_projections(inputs)

        std = {
            "available_capital": Decimal("80000.00"),
            "equipment_and_setup_cost": Decimal("70000.00"),
            "initial_inventory_cost": Decimal("25000.00"),
            "licensing_and_contingency": Decimal("5000.00"),
            "monthly_raw_material_cost": Decimal("40000.00"),
            "monthly_rent_and_utilities": Decimal("4000.00"),
            "monthly_salaries_and_labour": Decimal("8000.00"),
            "monthly_transport_and_logistics": Decimal("2000.00"),
            "monthly_marketing_expense": Decimal("1000.00"),
            "monthly_other_expenses": Decimal("1000.00"),
            "estimated_selling_price_per_unit": Decimal("160.00"),
            "expected_monthly_sales_volume": Decimal("500.00"),
            "loan_amount": Decimal("50000.00"),
            "annual_interest_rate": Decimal("10.00"),
            "loan_tenure_months": 36,
            "working_capital_months": 3,
        }
        m = proj(std)
        exp_startup = Decimal("100000.00")
        exp_opex = Decimal("56000.00")
        exp_rev = Decimal("80000.00")
        exp_ebitda = Decimal("24000.00")
        exp_margin = Decimal("30.00")
        exp_wc = Decimal("168000.00")
        exp_payback = Decimal("4.2")
        checks = [
            ("total_startup_investment == 100000", m["total_startup_investment"] == exp_startup),
            ("total_monthly_operating_cost == 56000", m["total_monthly_operating_cost"] == exp_opex),
            ("estimated_monthly_revenue == 80000", m["estimated_monthly_revenue"] == exp_rev),
            ("estimated_monthly_ebitda == 24000", m["estimated_monthly_ebitda"] == exp_ebitda),
            ("profit_margin_percent == 30", m["profit_margin_percent"] == exp_margin),
            ("working_capital == 168000", m["working_capital_requirement"] == exp_wc),
            ("payback == 4.2", m["payback_period_months"] == exp_payback),
            ("break_even_units 0 < x < 500", Decimal("0") < m["break_even_units"] < Decimal("500")),
            ("net_profit = ebitda - interest", m["estimated_monthly_net_profit"] == m["estimated_monthly_ebitda"] - m["monthly_interest_cost"]),
        loan = calculate_loan_schedule(Decimal("50000.00"), Decimal("10.00"), 36)
        r = (Decimal("10") / Decimal("100")) / Decimal("12")
        one_plus_r = (Decimal("1") + r) ** 36
        exp_emi = (Decimal("50000") * r * one_plus_r / (one_plus_r - Decimal("1"))).quantize(Decimal("0.01"))
        checks.append(("loan EMI matches formula", money(loan["monthly_loan_emi"]) == money(exp_emi)))

        zero_inputs = dict(std)
        zero_inputs.update(
            {
                "estimated_selling_price_per_unit": Decimal("0.00"),
                "expected_monthly_sales_volume": Decimal("0.00"),
                "monthly_raw_material_cost": Decimal("0.00"),
                "monthly_rent_and_utilities": Decimal("0.00"),
                "monthly_salaries_and_labour": Decimal("0.00"),
                "loan_amount": Decimal("0.00"),
            }
        )
        zm = proj(zero_inputs)
        checks.append(("zero inputs: no crash", True))
        checks.append(("zero inputs: revenue == 0", zm["estimated_monthly_revenue"] == ZERO))
        checks.append(("zero inputs: ebitda safe", zm["estimated_monthly_ebitda"] is not None))
        checks.append(("zero inputs: break_even None or zero", zm["break_even_units"] is None or zm["break_even_units"] == ZERO))

        zp = dict(std)
        zp["estimated_selling_price_per_unit"] = Decimal("0.00")
        zp["expected_monthly_sales_volume"] = Decimal("100.00")
        mzp = proj(zp)
        checks.append(("zero price: revenue == 0", mzp["estimated_monthly_revenue"] == ZERO))

        huge = dict(std)
        for f in ["equipment_and_setup_cost", "initial_inventory_cost", "loan_amount"]:
            huge[f] = Decimal("9999999999.99")
        mh = proj(huge)
        checks.append(("huge values: finite results", mh["total_startup_investment"].is_finite()))

        no_opex = dict(std)
        for f in ["monthly_raw_material_cost", "monthly_rent_and_utilities", "monthly_salaries_and_labour",
                  "monthly_transport_and_logistics", "monthly_marketing_expense", "monthly_other_expenses"]:
            no_opex[f] = Decimal("0.00")
        m2 = proj(no_opex)
        checks.append(("zero opex: margin == 100", m2["profit_margin_percent"] == Decimal("100.00")))

        sc = build_scenario_comparisons(std)
        checks.append(("scenarios: conservative < expected < optimistic revenue",
                       sc["conservative"]["estimated_monthly_revenue"] < sc["expected"]["estimated_monthly_revenue"] < sc["optimistic"]["estimated_monthly_revenue"]))

        failures = [c[0] for c in checks if not c[1]]
        record(
            "QA-FUNC-004",
            "Financial Structuring",
            "Startup investment, opex, revenue, EBITDA, margin, break-even, payback, working capital, loan EMI, scenarios, edge cases (zero price/volume/opex, huge values)",
            "Direct service calls (no HTTP)",
            "Call calculate_financial_projections / calculate_loan_schedule / build_scenario_comparisons with standard and edge-case inputs; compare to independent hand calculations",
            "All metrics match independent hand calculations; division-by-zero guarded; scenarios ordered correctly",
            "PASS" if not failures else "FAIL",
            "CRITICAL" if failures else "LOW",
            "; ".join(failures) if failures else f"{len(checks)} calculation checks verified (standard + edge cases)",
        )

        ]

            "Authenticated user u1; AI_PROVIDER_ENABLED=False",
            "Call generate_rule_based_recommendations and call_external_ai_provider directly; POST advisory form valid and invalid; GET detail",
            "Fallback labelled Rule-Based with >=2 recommendations; invalid budget (<₹1,000) rejected; plan and recommendations persisted; detail renders",
            "PARTIAL" if core_ok and failures else ("PASS" if not failures else "FAIL"),
            "HIGH" if not rb_ok or not persisted else "MEDIUM",
            "; ".join(failures) if failures else f"Advisory verified: fallback={rb_ok}, ai_off={ai_ok}, plans={persisted}, recs={recs_count}",
        )

            "Registration, login, logout, duplicate/invalid handling, protected access",
            "Clean test DB",
            "POST register (valid/duplicate/invalid email); POST login (valid/invalid); GET logout; GET dashboard anonymous",
            "All auth flows behave correctly; duplicate email/username blocked; invalid credentials rejected; anonymous users redirected to login",
            "PASS" if not failures else "FAIL",
            "HIGH" if failures else "LOW",
            "; ".join(failures) if failures else "All authentication flows verified",
        )

        )

                        f"{name} ({url}): authenticated expected 200/302, got {resp.status_code}"
                    )

class GramVentureFunctionalAudit(TestCase):
    """End-to-end functional audit executed against the real view layer."""

    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)
        self.u1 = User.objects.create_user(
            username="entrepreneur_a", email="a@example.com", password="SecurePass@2026"
        )
        self.u2 = User.objects.create_user(
            username="entrepreneur_b", email="b@example.com", password="SecurePass@2026"
        )
        self.client.login(username="entrepreneur_a", password="SecurePass@2026")
        ensure_default_schemes_seeded()
