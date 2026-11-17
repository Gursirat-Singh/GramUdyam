from decimal import Decimal
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from financial_planning.models import FinancialPlan


class DashboardViewTests(TestCase):
    """Tests public landing page and authenticated dynamic entrepreneur dashboard."""

    def test_public_home_page_renders(self):
        resp = self.client.get(reverse("home"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "GramUdyam")

    def test_authenticated_dashboard_displays_dynamic_metrics(self):
        user = User.objects.create_user(username="dash_user", first_name="Karamjit", password="Password@123")
        FinancialPlan.objects.create(
            user=user,
            title="Test Dairy Unit",
            available_capital=Decimal("90000.00"),
            equipment_and_setup_cost=Decimal("65000.00"),
            initial_inventory_cost=Decimal("15000.00"),
            monthly_raw_material_cost=Decimal("30000.00"),
            monthly_rent_and_utilities=Decimal("5000.00"),
            estimated_selling_price_per_unit=Decimal("100.00"),
            expected_monthly_sales_volume=Decimal("550.00"),
        )
        self.client.login(username="dash_user", password="Password@123")
        resp = self.client.get(reverse("dashboard:index"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Karamjit")
        self.assertContains(resp, "80000.00")  # Startup capital = 65000 + 15000
        self.assertContains(resp, "55000.00")  # Monthly revenue = 100 * 550
