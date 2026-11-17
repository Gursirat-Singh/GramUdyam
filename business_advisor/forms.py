from decimal import Decimal
from django import forms
from django.core.exceptions import ValidationError
from accounts.models import INDIAN_STATE_CHOICES
from business_advisor.models import BusinessPlan, BUSINESS_CATEGORY_CHOICES


class BusinessAdvisoryForm(forms.ModelForm):
    '''Server-validated form for generating hyper-local rural business recommendations.'''
    state = forms.ChoiceField(choices=INDIAN_STATE_CHOICES, label="State / Union Territory")
    business_category = forms.ChoiceField(choices=BUSINESS_CATEGORY_CHOICES, label="Business Sector / Category")

    class Meta:
        model = BusinessPlan
        fields = (
            "title",
            "state",
            "district",
            "village_or_town",
            "investment_budget",
            "business_category",
            "business_idea",
            "existing_skills",
            "existing_resources",
            "target_customers",
            "business_objectives",
            "constraints",
        )
        widgets = {
            "existing_skills": forms.Textarea(attrs={"rows": 3, "placeholder": "e.g., Dairy animal care, basic accounting, operating flour mill, tailoring..."}),
            "existing_resources": forms.Textarea(attrs={"rows": 2, "placeholder": "e.g., 250 sq.ft. roadside room, single-phase power connection, two-wheeler..."}),
            "business_objectives": forms.Textarea(attrs={"rows": 3, "placeholder": "e.g., Earn ₹18,000–₹25,000 net monthly income within 6 months and employ 1 family member..."}),
            "constraints": forms.Textarea(attrs={"rows": 2, "placeholder": "e.g., 4-hour afternoon power cuts, 12 km distance to nearest wholesale mandi..."}),
        }

    def clean_investment_budget(self):
        budget = self.cleaned_data.get("investment_budget")
        if budget is None:
            raise ValidationError("Please enter your available investment budget.")
        if budget < Decimal("1000.00"):
            raise ValidationError("Investment budget must be at least ₹1,000 to structure a viable micro-enterprise.")
        if budget > Decimal("50000000.00"):
            raise ValidationError("Investment budget exceeds the rural micro-enterprise cap (₹5 Crore).")
        return budget

    def clean_district(self):
        d = (self.cleaned_data.get("district") or "").strip()
        if len(d) < 2:
            raise ValidationError("Please enter a valid district name.")
        return d

    def clean_village_or_town(self):
        v = (self.cleaned_data.get("village_or_town") or "").strip()
        if len(v) < 2:
            raise ValidationError("Please enter your village, block, or town name.")
        return v
