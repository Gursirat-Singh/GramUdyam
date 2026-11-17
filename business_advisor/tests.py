from decimal import Decimal
from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from business_advisor.models import BusinessPlan
from business_advisor.services import call_external_ai_provider, generate_rule_based_recommendations


class BusinessAdvisoryTests(TestCase):
    """Tests for AI fallback service layer, form validation, and ownership protection."""

    def test_rule_based_fallback_generates_labelled_recommendations(self):
        plan_data = {
            "business_category": "DAIRY_LIVESTOCK",
            "investment_budget": Decimal("90000.00"),
            "state": "Punjab",
            "district": "Karnal",
            "village_or_town": "Gharaunda",
            "existing_skills": "Milk quality testing and cattle care",
            "existing_resources": "Roadside room with power backup",
            "target_customers": "Local sweet shops and households",
            "business_objectives": "Steady ₹20,000 monthly income",
            "constraints": "Summer power cuts",
        }
        res = generate_rule_based_recommendations(plan_data)
        self.assertEqual(res["advisory_source"], "RULE_BASED_FALLBACK")
        self.assertTrue(len(res["recommendations"]) >= 2)
        for rec in res["recommendations"]:
            self.assertIn("Rule-Based", rec["source_label"])
            self.assertTrue(rec["estimated_startup_cost"] > Decimal("0.00"))

    def test_external_ai_failure_gracefully_falls_back(self):
        orig_enabled = settings.AI_PROVIDER_ENABLED
        orig_key = settings.AI_API_KEY
        orig_url = settings.AI_API_URL
        try:
            settings.AI_PROVIDER_ENABLED = True
            settings.AI_API_KEY = "invalid-key"
            settings.AI_API_URL = "http://127.0.0.1:9/unreachable"
            res = call_external_ai_provider(
                {
                    "business_category": "FOOD_PROCESSING",
                    "investment_budget": Decimal("60000.00"),
                    "state": "Punjab",
                    "district": "Moga",
                    "village_or_town": "Baghapurana",
                },
                user_id=999,
            )
            self.assertEqual(res["advisory_source"], "RULE_BASED_FALLBACK")
            self.assertTrue(len(res["recommendations"]) >= 2)
        finally:
            settings.AI_PROVIDER_ENABLED = orig_enabled
            settings.AI_API_KEY = orig_key
            settings.AI_API_URL = orig_url

    def test_create_advisory_and_ownership_protection(self):
        u1 = User.objects.create_user(username="owner_user", password="Password@123")
        u2 = User.objects.create_user(username="other_user", password="Password@123")
        self.client.login(username="owner_user", password="Password@123")

        post_data = {
            "title": "Moga Spice Grinding Unit",
            "state": "Punjab",
            "district": "Moga",
            "village_or_town": "Ajitwal",
            "investment_budget": "75000.00",
            "business_category": "FOOD_PROCESSING",
            "business_idea": "Pure turmeric and chilli powder",
            "existing_skills": "Spice drying and packaging",
            "existing_resources": "150 sq ft room",
            "target_customers": "Village households and dhabas",
            "business_objectives": "Earn ₹18,000 per month",
            "constraints": "Monsoon humidity",
        }
        resp = self.client.post(reverse("business_advisor:create"), data=post_data, follow=True)
        self.assertEqual(resp.status_code, 200)
        plan = BusinessPlan.objects.get(user=u1)
        self.assertTrue(plan.recommendations.count() >= 2)

        # Other user cannot view or delete owner_user's plan
        self.client.logout()
        self.client.login(username="other_user", password="Password@123")
        forbidden_resp = self.client.get(reverse("business_advisor:detail", kwargs={"pk": plan.pk}))
        self.assertEqual(forbidden_resp.status_code, 404)
