from django import forms
from django.core.exceptions import ValidationError
from accounts.models import INDIAN_STATE_CHOICES
from business_advisor.models import BUSINESS_CATEGORY_CHOICES, BusinessPlan
from market_insights.models import MarketObservation


class MarketObservationForm(forms.ModelForm):
    '''Form for logging hyper-local market observations (competitors, demand, suppliers, pricing).'''
    state = forms.ChoiceField(choices=INDIAN_STATE_CHOICES, label="State / UT")
    business_category = forms.ChoiceField(choices=BUSINESS_CATEGORY_CHOICES, label="Business Category")

    class Meta:
        model = MarketObservation
        fields = (
            "business_plan",
            "state",
            "district",
            "village_or_town",
            "business_category",
            "observation_type",
            "subject_name",
            "observed_price_or_metric",
            "competitor_count",
            "demand_level",
            "supplier_availability",
            "observed_date",
            "details",
        )
        widgets = {
            "details": forms.Textarea(attrs={"rows": 3, "placeholder": "Describe quality gaps, customer feedback, wholesale vs retail margin, or transport bottlenecks observed..."}),
            "observed_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if user is not None:
            self.fields["business_plan"].queryset = BusinessPlan.objects.filter(user=user)
            self.fields["business_plan"].required = False

    def clean_subject_name(self):
        name = (self.cleaned_data.get("subject_name") or "").strip()
        if len(name) < 2:
            raise ValidationError("Please enter the name of the product, competitor, or mandi observed.")
        return name
