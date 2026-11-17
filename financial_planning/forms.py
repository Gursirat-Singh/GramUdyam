from decimal import Decimal
from django import forms
from django.core.exceptions import ValidationError
from business_advisor.models import BusinessPlan
from financial_planning.models import FinancialPlan, FinancialExpense


class FinancialPlanForm(forms.ModelForm):
    '''Server-validated form for creating and editing a FinancialPlan.'''

    class Meta:
        model = FinancialPlan
        fields = (
            "title",
            "business_plan",
            "available_capital",
            "equipment_and_setup_cost",
            "initial_inventory_cost",
            "licensing_and_contingency",
            "monthly_raw_material_cost",
            "monthly_rent_and_utilities",
            "monthly_salaries_and_labour",
            "monthly_transport_and_logistics",
            "monthly_marketing_expense",
            "monthly_other_expenses",
            "estimated_selling_price_per_unit",
            "expected_monthly_sales_volume",
            "loan_amount",
            "annual_interest_rate",
            "loan_tenure_months",
            "working_capital_months",
            "notes",
        )
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 3, "placeholder": "Record supplier quotes, seasonal assumptions, or bank branch notes..."}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if user is not None:
            self.fields["business_plan"].queryset = BusinessPlan.objects.filter(user=user)
            self.fields["business_plan"].required = False

    def clean_estimated_selling_price_per_unit(self):
        price = self.cleaned_data.get("estimated_selling_price_per_unit")
        if price is None or price <= Decimal("0.00"):
            raise ValidationError("Selling price per unit must be greater than ₹0.00.")
        return price

    def clean_expected_monthly_sales_volume(self):
        vol = self.cleaned_data.get("expected_monthly_sales_volume")
        if vol is None or vol <= Decimal("0.00"):
            raise ValidationError("Expected monthly sales volume must be greater than 0.")
        return vol

    def clean_annual_interest_rate(self):
        rate = self.cleaned_data.get("annual_interest_rate")
        if rate is None:
            return Decimal("0.00")
        if rate < Decimal("0.00") or rate > Decimal("60.00"):
            raise ValidationError("Annual interest rate must be between 0% and 60%.")
        return rate

    def clean_loan_tenure_months(self):
        tenure = self.cleaned_data.get("loan_tenure_months")
        if tenure is None or tenure < 1 or tenure > 240:
            raise ValidationError("Loan tenure must be between 1 and 240 months.")
        return tenure

    def clean(self):
        cleaned = super().clean()
        non_negative_fields = [
            "available_capital",
            "equipment_and_setup_cost",
            "initial_inventory_cost",
            "licensing_and_contingency",
            "monthly_raw_material_cost",
            "monthly_rent_and_utilities",
            "monthly_salaries_and_labour",
            "monthly_transport_and_logistics",
            "monthly_marketing_expense",
            "monthly_other_expenses",
            "loan_amount",
        ]
        for fname in non_negative_fields:
            val = cleaned.get(fname)
            if val is not None and val < Decimal("0.00"):
                self.add_error(fname, "Monetary amounts cannot be negative.")
        return cleaned


class FinancialExpenseForm(forms.ModelForm):
    '''Form for adding itemized expense breakdowns to a FinancialPlan.'''

    class Meta:
        model = FinancialExpense
        fields = ("expense_type", "category", "description", "amount", "is_essential")

    def clean_amount(self):
        amt = self.cleaned_data.get("amount")
        if amt is None or amt <= Decimal("0.00"):
            raise ValidationError("Expense amount must be greater than ₹0.00.")
        return amt
