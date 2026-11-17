'''
Decimal-based Financial Structuring, Break-Even, Loan Amortization, and
3-Scenario Comparison Engine for Rural Micro-Entrepreneurs.

All monetary calculations strictly use Python's `decimal.Decimal` with explicit
quantization (`0.01`) and safe guards against division by zero, negative inputs,
or unrealistic assumptions.
'''
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation

ZERO = Decimal("0.00")
ONE_HUNDRED = Decimal("100.00")
CENT = Decimal("0.01")
TENTH = Decimal("0.1")


def to_decimal(val, default=ZERO):
    if val is None or val == "":
        return default
    if isinstance(val, Decimal):
        return val.quantize(CENT, rounding=ROUND_HALF_UP)
    try:
        d = Decimal(str(val))
        if not d.is_finite():
            return default
        return d.quantize(CENT, rounding=ROUND_HALF_UP)
    except (InvalidOperation, ValueError, TypeError):
        return default


def calculate_loan_schedule(loan_amount, annual_interest_rate, tenure_months):
    '''
    Calculates monthly simple/average interest burden and reducing-balance EMI
    using Decimal arithmetic. Safely handles zero loan or zero interest rate.
    '''
    principal = max(ZERO, to_decimal(loan_amount))
    rate_pa = max(ZERO, to_decimal(annual_interest_rate))
    months = max(1, int(tenure_months or 36))

    if principal <= ZERO:
        return {
            "monthly_interest_cost": ZERO,
            "monthly_loan_emi": ZERO,
            "total_repayment": ZERO,
            "total_interest_payable": ZERO,
        }

    if rate_pa <= ZERO:
        emi = (principal / Decimal(str(months))).quantize(CENT, rounding=ROUND_HALF_UP)
        return {
            "monthly_interest_cost": ZERO,
            "monthly_loan_emi": emi,
            "total_repayment": principal,
            "total_interest_payable": ZERO,
        }

    # Monthly interest rate r = (annual_interest_rate / 100) / 12
    r = (rate_pa / ONE_HUNDRED) / Decimal("12")
    # First-month / conservative monthly interest cost = P * r
    first_month_interest = (principal * r).quantize(CENT, rounding=ROUND_HALF_UP)

    # Reducing balance EMI = P * r * (1+r)^n / ((1+r)^n - 1)
    one_plus_r_pow_n = (Decimal("1") + r) ** months
    denom = one_plus_r_pow_n - Decimal("1")
    if denom <= ZERO:
        emi = (principal / Decimal(str(months)) + first_month_interest).quantize(CENT, rounding=ROUND_HALF_UP)
    else:
        emi = (principal * r * one_plus_r_pow_n / denom).quantize(CENT, rounding=ROUND_HALF_UP)

    total_repayment = (emi * Decimal(str(months))).quantize(CENT, rounding=ROUND_HALF_UP)
    total_interest = max(ZERO, total_repayment - principal).quantize(CENT, rounding=ROUND_HALF_UP)
    avg_monthly_interest = (total_interest / Decimal(str(months))).quantize(CENT, rounding=ROUND_HALF_UP)

    return {
        "monthly_interest_cost": avg_monthly_interest,
        "first_month_interest": first_month_interest,
        "monthly_loan_emi": emi,
        "total_repayment": total_repayment,
        "total_interest_payable": total_interest,
    }


def calculate_financial_projections(plan_or_dict):
    '''
    Computes complete startup investment, operating cost, revenue, EBITDA, net profit,
    profit margin, break-even volume/revenue, payback timeline, working capital, and
    risk indicators from either a FinancialPlan instance or a dictionary of inputs.
    '''
    def _get(field_name, default=ZERO):
        if isinstance(plan_or_dict, dict):
            return plan_or_dict.get(field_name, default)
        return getattr(plan_or_dict, field_name, default)

    available_capital = max(ZERO, to_decimal(_get("available_capital")))
    equipment_cost = max(ZERO, to_decimal(_get("equipment_and_setup_cost")))
    inventory_cost = max(ZERO, to_decimal(_get("initial_inventory_cost")))
    licensing_cost = max(ZERO, to_decimal(_get("licensing_and_contingency")))

    raw_materials = max(ZERO, to_decimal(_get("monthly_raw_material_cost")))
    rent_utilities = max(ZERO, to_decimal(_get("monthly_rent_and_utilities")))
    salaries_labour = max(ZERO, to_decimal(_get("monthly_salaries_and_labour")))
    transport_logistics = max(ZERO, to_decimal(_get("monthly_transport_and_logistics")))
    marketing = max(ZERO, to_decimal(_get("monthly_marketing_expense")))
    other_expenses = max(ZERO, to_decimal(_get("monthly_other_expenses")))

    selling_price = max(ZERO, to_decimal(_get("estimated_selling_price_per_unit")))
    sales_volume = max(ZERO, to_decimal(_get("expected_monthly_sales_volume")))

    loan_amount = max(ZERO, to_decimal(_get("loan_amount")))
    interest_rate = max(ZERO, to_decimal(_get("annual_interest_rate")))
    loan_tenure = max(1, int(_get("loan_tenure_months", 36) or 36))
    wc_months = max(1, int(_get("working_capital_months", 3) or 3))

    # 1. Total Startup Investment
    total_startup_investment = (equipment_cost + inventory_cost + licensing_cost).quantize(CENT, rounding=ROUND_HALF_UP)

    # 2. Monthly Operating Costs (Fixed vs Variable)
    # Raw materials + 50% of transport are treated as variable with volume; rest as fixed monthly operating overhead
    variable_monthly_cost = (raw_materials + (transport_logistics * Decimal("0.50"))).quantize(CENT, rounding=ROUND_HALF_UP)
    fixed_monthly_cost = (
        rent_utilities
        + salaries_labour
        + (transport_logistics * Decimal("0.50"))
        + marketing
        + other_expenses
    ).quantize(CENT, rounding=ROUND_HALF_UP)
    total_monthly_operating_cost = (
        raw_materials + rent_utilities + salaries_labour + transport_logistics + marketing + other_expenses
    ).quantize(CENT, rounding=ROUND_HALF_UP)

    # 3. Estimated Monthly Revenue
    estimated_monthly_revenue = (selling_price * sales_volume).quantize(CENT, rounding=ROUND_HALF_UP)

    # 4. Estimated Monthly Profit Before Taxes and Financing Costs (EBITDA)
    estimated_monthly_ebitda = (estimated_monthly_revenue - total_monthly_operating_cost).quantize(CENT, rounding=ROUND_HALF_UP)

    # 5. Financing Costs & Net Profit
    loan_metrics = calculate_loan_schedule(loan_amount, interest_rate, loan_tenure)
    monthly_interest_cost = loan_metrics["monthly_interest_cost"]
    monthly_loan_emi = loan_metrics["monthly_loan_emi"]
    estimated_monthly_net_profit = (estimated_monthly_ebitda - monthly_interest_cost).quantize(CENT, rounding=ROUND_HALF_UP)
    monthly_cash_surplus_after_emi = (estimated_monthly_ebitda - monthly_loan_emi).quantize(CENT, rounding=ROUND_HALF_UP)

    # 6. Operating Profit Margin (%)
    if estimated_monthly_revenue > ZERO:
        profit_margin_percent = ((estimated_monthly_ebitda / estimated_monthly_revenue) * ONE_HUNDRED).quantize(
            CENT, rounding=ROUND_HALF_UP
        )
        # Clamp extreme negative margins to fit max_digits=7 (-999.99 to 100.00)
        profit_margin_percent = max(Decimal("-999.99"), min(ONE_HUNDRED, profit_margin_percent))
    else:
        profit_margin_percent = ZERO

    # 7. Break-Even Analysis
    if sales_volume > ZERO:
        unit_variable_cost = (variable_monthly_cost / sales_volume).quantize(CENT, rounding=ROUND_HALF_UP)
    else:
        unit_variable_cost = ZERO

    unit_contribution_margin = (selling_price - unit_variable_cost).quantize(CENT, rounding=ROUND_HALF_UP)

    if unit_contribution_margin > ZERO:
        if fixed_monthly_cost > ZERO:
            break_even_units = (fixed_monthly_cost / unit_contribution_margin).quantize(CENT, rounding=ROUND_HALF_UP)
            break_even_revenue = (break_even_units * selling_price).quantize(CENT, rounding=ROUND_HALF_UP)
            break_even_status = "VIABLE_CONTRIBUTION"
        else:
            break_even_units = ZERO
            break_even_revenue = ZERO
            break_even_status = "ZERO_FIXED_COST"
    else:
        break_even_units = None
        break_even_revenue = None
        break_even_status = "NEGATIVE_UNIT_CONTRIBUTION"

    # Approximate break-even / capital payback timeline (months to recover startup investment from EBITDA)
    if estimated_monthly_ebitda > ZERO and total_startup_investment > ZERO:
        payback_period_months = (total_startup_investment / estimated_monthly_ebitda).quantize(
            TENTH, rounding=ROUND_HALF_UP
        )
        payback_period_months = min(Decimal("999.9"), payback_period_months)
    elif total_startup_investment == ZERO and estimated_monthly_ebitda > ZERO:
        payback_period_months = Decimal("0.0")
    else:
        payback_period_months = None

    # 8. Working Capital & Capital Structure
    working_capital_requirement = (total_monthly_operating_cost * Decimal(str(wc_months))).quantize(
        CENT, rounding=ROUND_HALF_UP
    )
    total_capital_required = (total_startup_investment + working_capital_requirement).quantize(
        CENT, rounding=ROUND_HALF_UP
    )
    total_funding_available = (available_capital + loan_amount).quantize(CENT, rounding=ROUND_HALF_UP)
    capital_gap = max(ZERO, total_capital_required - total_funding_available).quantize(CENT, rounding=ROUND_HALF_UP)

    # 9. Risk Assessment Classification & Warnings
    warnings = []
    if estimated_monthly_ebitda <= ZERO:
        warnings.append(
            "Operating Loss Warning: Monthly operating costs exceed or equal estimated monthly revenue."
        )
    if break_even_status == "NEGATIVE_UNIT_CONTRIBUTION":
        warnings.append(
            f"Unit Economics Alert: Variable cost per unit (₹{unit_variable_cost}) is greater than or equal to selling price (₹{selling_price}). Increase price or reduce raw material cost."
        )
    if monthly_loan_emi > ZERO and monthly_cash_surplus_after_emi < ZERO:
        warnings.append(
            f"Debt Service Warning: Monthly loan EMI (₹{monthly_loan_emi}) exceeds monthly operating profit (₹{estimated_monthly_ebitda})."
        )
    if capital_gap > ZERO:
        warnings.append(
            f"Funding Gap: Total capital + {wc_months}-month working capital buffer requires ₹{total_capital_required}, leaving an unfunded gap of ₹{capital_gap}."
        )

    if estimated_monthly_ebitda <= ZERO or monthly_cash_surplus_after_emi < ZERO or capital_gap > (total_capital_required * Decimal("0.25")):
        risk_assessment = "HIGH"
    elif profit_margin_percent < Decimal("15.00") or capital_gap > ZERO or (payback_period_months and payback_period_months > Decimal("24.0")):
        risk_assessment = "MODERATE"
    else:
        risk_assessment = "LOW"

    return {
        "total_startup_investment": total_startup_investment,
        "fixed_monthly_cost": fixed_monthly_cost,
        "variable_monthly_cost": variable_monthly_cost,
        "total_monthly_operating_cost": total_monthly_operating_cost,
        "estimated_monthly_revenue": estimated_monthly_revenue,
        "estimated_monthly_ebitda": estimated_monthly_ebitda,
        "monthly_interest_cost": monthly_interest_cost,
        "monthly_loan_emi": monthly_loan_emi,
        "total_loan_repayment": loan_metrics["total_repayment"],
        "total_interest_payable": loan_metrics["total_interest_payable"],
        "estimated_monthly_net_profit": estimated_monthly_net_profit,
        "monthly_cash_surplus_after_emi": monthly_cash_surplus_after_emi,
        "profit_margin_percent": profit_margin_percent,
        "unit_variable_cost": unit_variable_cost,
        "unit_contribution_margin": unit_contribution_margin,
        "break_even_units": break_even_units,
        "break_even_revenue": break_even_revenue,
        "break_even_status": break_even_status,
        "payback_period_months": payback_period_months,
        "working_capital_requirement": working_capital_requirement,
        "total_capital_required": total_capital_required,
        "total_funding_available": total_funding_available,
        "capital_gap": capital_gap,
        "risk_assessment": risk_assessment,
        "warnings": warnings,
    }


def build_scenario_comparisons(plan_or_dict):
    '''
    Generates Conservative, Expected (Base), and Optimistic scenario projections
    so entrepreneurs can stress-test volume drops or input cost inflation.
    '''
    def _extract_dict(src):
        fields = [
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
        ]
        if isinstance(src, dict):
            return {f: src.get(f) for f in fields}
        return {f: getattr(src, f, None) for f in fields}

    base_inputs = _extract_dict(plan_or_dict)
    base_vol = to_decimal(base_inputs["expected_monthly_sales_volume"])
    base_price = to_decimal(base_inputs["estimated_selling_price_per_unit"])
    base_raw = to_decimal(base_inputs["monthly_raw_material_cost"])
    base_trans = to_decimal(base_inputs["monthly_transport_and_logistics"])

    # Conservative Scenario: -25% sales volume, -5% selling price, +10% raw material/transport per unit
    # Since volume is 75%, total raw material cost scales by 0.75 * 1.10 = 0.825
    cons_inputs = dict(base_inputs)
    cons_inputs["expected_monthly_sales_volume"] = (base_vol * Decimal("0.75")).quantize(CENT, rounding=ROUND_HALF_UP)
    cons_inputs["estimated_selling_price_per_unit"] = (base_price * Decimal("0.95")).quantize(CENT, rounding=ROUND_HALF_UP)
    cons_inputs["monthly_raw_material_cost"] = (base_raw * Decimal("0.825")).quantize(CENT, rounding=ROUND_HALF_UP)
    cons_inputs["monthly_transport_and_logistics"] = (base_trans * Decimal("1.05")).quantize(CENT, rounding=ROUND_HALF_UP)

    # Optimistic Scenario: +25% sales volume, +5% selling price, raw materials scale with volume * 0.96 bulk efficiency
    opt_inputs = dict(base_inputs)
    opt_inputs["expected_monthly_sales_volume"] = (base_vol * Decimal("1.25")).quantize(CENT, rounding=ROUND_HALF_UP)
    opt_inputs["estimated_selling_price_per_unit"] = (base_price * Decimal("1.05")).quantize(CENT, rounding=ROUND_HALF_UP)
    opt_inputs["monthly_raw_material_cost"] = (base_raw * Decimal("1.20")).quantize(CENT, rounding=ROUND_HALF_UP)
    opt_inputs["monthly_transport_and_logistics"] = (base_trans * Decimal("1.10")).quantize(CENT, rounding=ROUND_HALF_UP)

    cons_metrics = calculate_financial_projections(cons_inputs)
    base_metrics = calculate_financial_projections(base_inputs)
    opt_metrics = calculate_financial_projections(opt_inputs)

    return {
        "conservative": {
            "label": "Conservative (Lean / Slow Season)",
            "assumptions_note": "Sales Volume -25%, Selling Price -5%, Unit Input Cost +10%",
            "sales_volume": cons_inputs["expected_monthly_sales_volume"],
            "selling_price": cons_inputs["estimated_selling_price_per_unit"],
            **cons_metrics,
        },
        "expected": {
            "label": "Expected (User Baseline)",
            "assumptions_note": "100% of User-Entered Volume, Price, and Cost Assumptions",
            "sales_volume": base_vol,
            "selling_price": base_price,
            **base_metrics,
        },
        "optimistic": {
            "label": "Optimistic (Peak / High Demand)",
            "assumptions_note": "Sales Volume +25%, Selling Price +5%, 4% Bulk Input Efficiency",
            "sales_volume": opt_inputs["expected_monthly_sales_volume"],
            "selling_price": opt_inputs["estimated_selling_price_per_unit"],
            **opt_metrics,
        },
    }


def get_formula_explanations():
    '''Returns transparent formula definitions displayed in financial views and reports.'''
    return [
        {
            "metric": "Total Startup Investment",
            "formula": "Equipment & Setup Cost + Initial Opening Inventory + Licensing & Contingency",
            "explanation": "One-time capital expenditure required before commercial operations begin.",
        },
        {
            "metric": "Total Monthly Operating Cost",
            "formula": "Raw Materials + Rent & Utilities + Salaries & Labour + Transport & Logistics + Marketing + Other Recurring Costs",
            "explanation": "Recurring monthly cash outflow required to produce goods/services and keep the unit running.",
        },
        {
            "metric": "Estimated Monthly Revenue",
            "formula": "Estimated Selling Price per Unit × Expected Monthly Sales Volume",
            "explanation": "Gross monthly sales inflow assuming all billed sales are collected.",
        },
        {
            "metric": "Monthly Operating Profit (EBITDA)",
            "formula": "Estimated Monthly Revenue − Total Monthly Operating Cost",
            "explanation": "Monthly profit generated from core operations before loan interest/EMI and taxes.",
        },
        {
            "metric": "Operating Profit Margin (%)",
            "formula": "(Monthly Operating Profit ÷ Estimated Monthly Revenue) × 100",
            "explanation": "Percentage of each rupee of sales retained as operating profit.",
        },
        {
            "metric": "Break-Even Sales Volume (Units)",
            "formula": "Fixed Monthly Operating Costs ÷ (Selling Price per Unit − Variable Cost per Unit)",
            "explanation": "Minimum monthly units that must be sold so revenue exactly covers all monthly costs.",
        },
        {
            "metric": "Startup Payback Timeline (Months)",
            "formula": "Total Startup Investment ÷ Monthly Operating Profit (EBITDA)",
            "explanation": "Approximate number of profitable operating months needed to recover initial startup capital.",
        },
        {
            "metric": "Working Capital Requirement",
            "formula": "Total Monthly Operating Cost × Working Capital Buffer Months",
            "explanation": "Cash reserve recommended to cover raw materials, wages, and bills during initial credit/lean cycles.",
        },
    ]
