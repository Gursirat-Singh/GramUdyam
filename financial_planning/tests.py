from decimal import Decimal
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from financial_planning.forms import FinancialPlanForm
from financial_planning.models import FinancialPlan
from financial_planning.services import (
    calculate_financial_projections,
    calculate_loan_schedule,
    build_scenario_comparisons,
)


class FinancialCalculationEngineTests(TestCase):
    """Unit tests for the Decimal-based financial calculation and scenario engine."""

    def test_standard_profitable_plan_calculations(self):
        inputs = {
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
        metrics = calculate_financial_projections(inputs)

        # Startup investment = 70000 + 25000 + 5000 = 100000.00
        self.assertEqual(metrics["total_startup_investment"], Decimal("100000.00"))
        # Monthly operating cost = 40000 + 4000 + 8000 + 2000 + 1000 + 1000 = 56000.00
        self.assertEqual(metrics["total_monthly_operating_cost"], Decimal("56000.00"))
        # Monthly revenue = 160 * 500 = 80000.00
        self.assertEqual(metrics["estimated_monthly_revenue"], Decimal("80000.00"))
        # EBITDA = 80000 - 56000 = 24000.00
        self.assertEqual(metrics["estimated_monthly_ebitda"], Decimal("24000.00"))
        # Margin = (24000 / 80000) * 100 = 30.00%
        self.assertEqual(metrics["profit_margin_percent"], Decimal("30.00"))
        # Working capital (3 months) = 56000 * 3 = 168000.00
        self.assertEqual(metrics["working_capital_requirement"], Decimal("168000.00"))
        # Break-even units must be positive and less than expected volume (500)
        self.assertIsNotNone(metrics["break_even_units"])
        self.assertTrue(Decimal("0.00") < metrics["break_even_units"] < Decimal("500.00"))
        # Payback period = 100000 / 24000 = 4.2 months
        self.assertEqual(metrics["payback_period_months"], Decimal("4.2"))

    def test_zero_denominator_and_negative_contribution_margin_safety(self):
        inputs = {
            "available_capital": Decimal("10000.00"),
            "equipment_and_setup_cost": Decimal("20000.00"),
            "initial_inventory_cost": Decimal("5000.00"),
            "licensing_and_contingency": Decimal("0.00"),
            "monthly_raw_material_cost": Decimal("30000.00"),
            "monthly_rent_and_utilities": Decimal("5000.00"),
            "monthly_salaries_and_labour": Decimal("0.00"),
            "monthly_transport_and_logistics": Decimal("0.00"),
            "monthly_marketing_expense": Decimal("0.00"),
            "monthly_other_expenses": Decimal("0.00"),
            "estimated_selling_price_per_unit": Decimal("50.00"),
            "expected_monthly_sales_volume": Decimal("500.00"),  # Revenue 25000 < Raw material 30000
            "loan_amount": Decimal("0.00"),
            "annual_interest_rate": Decimal("0.00"),
            "loan_tenure_months": 12,
            "working_capital_months": 2,
        }
        metrics = calculate_financial_projections(inputs)
        self.assertEqual(metrics["estimated_monthly_ebitda"], Decimal("-10000.00"))
        self.assertIsNone(metrics["break_even_units"])
        self.assertIsNone(metrics["payback_period_months"])
        self.assertEqual(metrics["risk_assessment"], "HIGH")
        self.assertTrue(len(metrics["warnings"]) >= 2)

    def test_loan_schedule_zero_and_positive_interest(self):
        zero_loan = calculate_loan_schedule(Decimal("0.00"), Decimal("12.00"), 24)
        self.assertEqual(zero_loan["monthly_loan_emi"], Decimal("0.00"))

        zero_interest = calculate_loan_schedule(Decimal("24000.00"), Decimal("0.00"), 24)
        self.assertEqual(zero_interest["monthly_loan_emi"], Decimal("1000.00"))

        std_loan = calculate_loan_schedule(Decimal("100000.00"), Decimal("12.00"), 12)
        self.assertTrue(std_loan["monthly_loan_emi"] > Decimal("8333.33"))
        self.assertTrue(std_loan["total_interest_payable"] > Decimal("0.00"))

    def test_three_scenario_comparisons_ordering(self):
        inputs = {
            "available_capital": Decimal("50000.00"),
            "equipment_and_setup_cost": Decimal("40000.00"),
            "initial_inventory_cost": Decimal("10000.00"),
            "licensing_and_contingency": Decimal("2000.00"),
            "monthly_raw_material_cost": Decimal("20000.00"),
            "monthly_rent_and_utilities": Decimal("3000.00"),
            "monthly_salaries_and_labour": Decimal("5000.00"),
            "monthly_transport_and_logistics": Decimal("1000.00"),
            "monthly_marketing_expense": Decimal("500.00"),
            "monthly_other_expenses": Decimal("500.00"),
            "estimated_selling_price_per_unit": Decimal("100.00"),
            "expected_monthly_sales_volume": Decimal("450.00"),
            "loan_amount": Decimal("0.00"),
            "annual_interest_rate": Decimal("0.00"),
            "loan_tenure_months": 24,
            "working_capital_months": 3,
        }
        scenarios = build_scenario_comparisons(inputs)
        self.assertIn("conservative", scenarios)
        self.assertIn("expected", scenarios)
        self.assertIn("optimistic", scenarios)
        self.assertTrue(
            scenarios["conservative"]["estimated_monthly_revenue"]
            < scenarios["expected"]["estimated_monthly_revenue"]
            < scenarios["optimistic"]["estimated_monthly_revenue"]
        )
        self.assertTrue(
            scenarios["conservative"]["estimated_monthly_ebitda"]
            < scenarios["expected"]["estimated_monthly_ebitda"]
            < scenarios["optimistic"]["estimated_monthly_ebitda"]
        )

    def test_financial_plan_form_server_validation(self):
        invalid_data = {
            "title": "Invalid Plan",
            "available_capital": "-500",
            "equipment_and_setup_cost": "10000",
            "initial_inventory_cost": "5000",
            "licensing_and_contingency": "0",
            "monthly_raw_material_cost": "5000",
            "monthly_rent_and_utilities": "1000",
            "monthly_salaries_and_labour": "0",
            "monthly_transport_and_logistics": "0",
            "monthly_marketing_expense": "0",
            "monthly_other_expenses": "0",
            "estimated_selling_price_per_unit": "0",
            "expected_monthly_sales_volume": "100",
            "loan_amount": "0",
            "annual_interest_rate": "85",
            "loan_tenure_months": "36",
            "working_capital_months": "3",
        }
        form = FinancialPlanForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn("estimated_selling_price_per_unit", form.errors)
        self.assertIn("annual_interest_rate", form.errors)

    def test_financial_plan_ownership_isolation(self):
        u1 = User.objects.create_user(username="farmer1", password="Password@123")
        u2 = User.objects.create_user(username="farmer2", password="Password@123")
        fplan = FinancialPlan.objects.create(
            user=u1,
            title="Farmer 1 Private Plan",
            available_capital=Decimal("50000.00"),
            equipment_and_setup_cost=Decimal("30000.00"),
            estimated_selling_price_per_unit=Decimal("120.00"),
            expected_monthly_sales_volume=Decimal("200.00"),
        )
        self.client.login(username="farmer2", password="Password@123")
        resp = self.client.get(reverse("financial_planning:detail", kwargs={"pk": fplan.pk}))
        self.assertEqual(resp.status_code, 404)
        edit_resp = self.client.get(reverse("financial_planning:edit", kwargs={"pk": fplan.pk}))
        self.assertEqual(edit_resp.status_code, 404)
