from decimal import Decimal
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from accounts.models import UserProfile


class AccountsAndProfileTests(TestCase):
    """Tests registration, authentication, profile persistence, and login_required protection."""

    def test_registration_creates_user_and_profile(self):
        resp = self.client.post(
            reverse("accounts:register"),
            data={
                "username": "harpreet_k",
                "first_name": "Harpreet",
                "last_name": "Kaur",
                "email": "harpreet@example.com",
                "state": "Punjab",
                "district": "Patiala",
                "village_or_town": "Nabha",
                "preferred_language": "pa",
                "available_capital": "95000.00",
                "skills": "Phulkari embroidery and tailoring",
                "business_interests": "Boutique and school uniforms",
                "password1": "StrongPass@2026",
                "password2": "StrongPass@2026",
            },
            follow=True,
        )
        self.assertEqual(resp.status_code, 200)
        user = User.objects.get(username="harpreet_k")
        profile = UserProfile.objects.get(user=user)
        self.assertEqual(profile.district, "Patiala")
        self.assertEqual(profile.available_capital, Decimal("95000.00"))

    def test_private_pages_redirect_anonymous_users(self):
        for route_name in ["dashboard:index", "business_advisor:list", "financial_planning:list", "market_insights:overview", "reports:list"]:
            resp = self.client.get(reverse(route_name))
            self.assertEqual(resp.status_code, 302)
            self.assertIn("/accounts/login/", resp.headers["Location"])
