from django import forms
from django.core.exceptions import ValidationError
from business_advisor.models import BusinessPlan
from financial_planning.models import FinancialPlan
from reports.models import Report


class ReportCreateForm(forms.ModelForm):
    '''Form for generating and saving a comprehensive business & financial report.'''

    class Meta:
        model = Report
        fields = ("title", "report_type", "business_plan", "financial_plan", "executive_summary")
        widgets = {
            "executive_summary": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Summarize your venture goal, target village market, funding requirement, and repayment plan...",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if user is not None:
            self.fields["business_plan"].queryset = BusinessPlan.objects.filter(user=user)
            self.fields["financial_plan"].queryset = FinancialPlan.objects.filter(user=user)
            self.fields["business_plan"].required = False
            self.fields["financial_plan"].required = False

    def clean(self):
        cleaned = super().clean()
        bp = cleaned.get("business_plan")
        fp = cleaned.get("financial_plan")
        if not bp and not fp:
            raise ValidationError("Please select at least one Business Plan or Financial Plan to include in the report.")
        return cleaned
