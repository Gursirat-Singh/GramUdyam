from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from market_insights.models import MarketObservation, FundingScheme
from market_insights.services import ensure_default_schemes_seeded


class MarketInsightsAndSchemesTests(TestCase):
    """Tests hyper-local market observations and government scheme guidance."""

    def setUp(self):
        super().setUp()
        self.user = User.objects.create_user(username="m_user", password="Password@123")
        self.client.login(username="m_user", password="Password@123")

    def test_schemes_seeding_and_listing(self):
        ensure_default_schemes_seeded()
        self.assertTrue(FundingScheme.objects.count() >= 6)
        resp = self.client.get(reverse("market_insights:schemes_list"))
        self.assertContains(resp, "PMEGP")
        self.assertContains(resp, "PMFME")

    def test_create_market_observation_labels_source_as_user_provided(self):
        resp = self.client.post(
            reverse("market_insights:add_observation"),
            data={
                "state": "Punjab",
                "district": "Sangrur",
                "village_or_town": "Dhuri",
                "business_category": "FOOD_PROCESSING",
                "observation_type": "PRICING",
                "subject_name": "Dhuri Mandi Jaggery Price Check",
                "observed_price_or_metric": "₹65/kg retail",
                "competitor_count": "3",
                "demand_level": "HIGH",
                "supplier_availability": "LOCAL_VILLAGE",
                "observed_date": "2026-10-15",
                "details": "High winter demand for chemical-free jaggery.",
            },
            follow=True,
        )
        self.assertEqual(resp.status_code, 200)
        obs = MarketObservation.objects.get(user=self.user)
        self.assertEqual(obs.data_source_type, "USER_PROVIDED")
