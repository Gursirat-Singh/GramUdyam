from decimal import Decimal
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from financial_planning.models import FinancialPlan
from reports.models import Report


class ReportsAndPdfExportTests(TestCase):
    """Tests report creation, ownership protection, and ReportLab PDF export."""

    def setUp(self):
        super().setUp()
        self.u1 = User.objects.create_user(username="rep_owner", password="Password@123")
        self.u2 = User.objects.create_user(username="rep_stranger", password="Password@123")
        self.fplan = FinancialPlan.objects.create(
            user=self.u1,
            title="Solar Dryer Financial Plan",
            available_capital=Decimal("75000.00"),
            equipment_and_setup_cost=Decimal("60000.00"),
            initial_inventory_cost=Decimal("10000.00"),
            monthly_raw_material_cost=Decimal("20000.00"),
            monthly_rent_and_utilities=Decimal("3000.00"),
            estimated_selling_price_per_unit=Decimal("200.00"),
            expected_monthly_sales_volume=Decimal("200.00"),
        )

    def test_create_report_and_export_pdf(self):
        self.client.login(username="rep_owner", password="Password@123")
        resp = self.client.post(
            reverse("reports:create"),
            data={
                "title": "Solar Dryer Bank Dossier",
                "report_type": "BANK_LOAN_PROPOSAL",
                "financial_plan": str(self.fplan.pk),
                "executive_summary": "Bank loan dossier for solar dryer unit.",
            },
            follow=True,
        )
        self.assertEqual(resp.status_code, 200)
        rep = Report.objects.get(user=self.u1)

        pdf_resp = self.client.get(reverse("reports:export_pdf", kwargs={"pk": rep.pk}))
        self.assertEqual(pdf_resp.status_code, 200)
        self.assertEqual(pdf_resp["Content-Type"], "application/pdf")
        self.assertTrue(pdf_resp.content.startswith(b"%PDF-"))

        # Stranger cannot access or download PDF
        self.client.logout()
        self.client.login(username="rep_stranger", password="Password@123")
        self.assertEqual(self.client.get(reverse("reports:detail", kwargs={"pk": rep.pk})).status_code, 404)
        self.assertEqual(self.client.get(reverse("reports:export_pdf", kwargs={"pk": rep.pk})).status_code, 404)
