import json
from decimal import Decimal
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from accounts.models import UserProfile
from business_advisor.models import BusinessPlan, BusinessRecommendation
from business_advisor.services import generate_rule_based_recommendations
from financial_planning.models import FinancialPlan, FinancialExpense
from financial_planning.services import (
    calculate_financial_projections,
    build_scenario_comparisons,
    get_formula_explanations,
)
from market_insights.models import MarketObservation
from market_insights.services import ensure_default_schemes_seeded
from reports.models import Report


class Command(BaseCommand):
    help = "Seeds verified government schemes and an optional demo rural entrepreneur account (demo_kisan)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--schemes-only",
            action="store_true",
            help="Seed only government funding schemes without creating the demo user.",
        )

    def handle(self, *args, **options):
        ensure_default_schemes_seeded()
        self.stdout.write(self.style.SUCCESS("Seeded 6 official government funding schemes."))

        if options.get("schemes_only"):
            return

        user, created = User.objects.get_or_create(
            username="demo_kisan",
            defaults={
                "first_name": "Gurpreet",
                "last_name": "Singh",
                "email": "gurpreet.samrala@example.com",
            },
        )
        if created:
            user.set_password("RuralPass@2026")
            user.save()

        UserProfile.objects.update_or_create(
            user=user,
            defaults={
                "state": "Punjab",
                "district": "Ludhiana",
                "village_or_town": "Samrala Block",
                "preferred_language": "pa",
                "available_capital": Decimal("85000.00"),
                "experience_years": 4,
                "shg_or_fpo_member": True,
                "skills": "Mustard & wheat post-harvest handling, operating mini expeller, dairy animal management",
                "business_interests": "Cold-press mustard oil unit, cattle feed cake, millet flour processing",
                "phone_number": "+91-9876543210",
            },
        )

        bp, bp_created = BusinessPlan.objects.get_or_create(
            user=user,
            title="Samrala Village Cold-Press Mustard Oil & Khal Unit",
            defaults={
                "business_category": "FOOD_PROCESSING",
                "business_idea": "Cold-press kachi ghani mustard oil & dairy oil-cake unit",
                "state": "Punjab",
                "district": "Ludhiana",
                "village_or_town": "Samrala Block",
                "investment_budget": Decimal("135000.00"),
                "existing_skills": "Operating agricultural machinery, local mandi procurement, retail distribution",
                "existing_resources": "250 sq.ft. pucca roadside room near village bus stand, 3-phase electricity meter",
                "target_customers": "Village households, local halwais, and 25 dairy farmers needing mustard oil-cake (khal)",
                "business_objectives": "Generate ₹22,000+ net monthly household income and process local sarson harvest",
                "constraints": "Seasonal spike in mustard seed prices between October and January",
                "advisory_source": "RULE_BASED_FALLBACK",
                "risk_level": "MODERATE",
            },
        )

        if bp_created or bp.recommendations.count() == 0:
            advisory = generate_rule_based_recommendations(
                {
                    "business_category": bp.business_category,
                    "investment_budget": bp.investment_budget,
                    "state": bp.state,
                    "district": bp.district,
                    "village_or_town": bp.village_or_town,
                    "existing_skills": bp.existing_skills,
                    "existing_resources": bp.existing_resources,
                    "target_customers": bp.target_customers,
                    "business_objectives": bp.business_objectives,
                    "constraints": bp.constraints,
                    "business_idea": bp.business_idea,
                }
            )
            for rec in advisory["recommendations"]:
                BusinessRecommendation.objects.create(business_plan=bp, **rec)

        fp, fp_created = FinancialPlan.objects.get_or_create(
            user=user,
            title="Cold-Press Mustard Oil & Khal Unit — Base Financial Model",
            defaults={
                "business_plan": bp,
                "available_capital": Decimal("85000.00"),
                "equipment_and_setup_cost": Decimal("78000.00"),
                "initial_inventory_cost": Decimal("32000.00"),
                "licensing_and_contingency": Decimal("8000.00"),
                "monthly_raw_material_cost": Decimal("62000.00"),
                "monthly_rent_and_utilities": Decimal("5500.00"),
                "monthly_salaries_and_labour": Decimal("9000.00"),
                "monthly_transport_and_logistics": Decimal("3200.00"),
                "monthly_marketing_expense": Decimal("1500.00"),
                "monthly_other_expenses": Decimal("1800.00"),
                "estimated_selling_price_per_unit": Decimal("175.00"),
                "expected_monthly_sales_volume": Decimal("650.00"),
                "loan_amount": Decimal("60000.00"),
                "annual_interest_rate": Decimal("9.50"),
                "loan_tenure_months": 36,
                "working_capital_months": 2,
                "notes": "Assumes 650 litres equivalent monthly sales (including oil-cake realization) at ₹175/unit.",
            },
        )
        if fp_created:
            FinancialExpense.objects.create(
                financial_plan=fp,
                expense_type="STARTUP",
                category="Machinery",
                description="3 HP Cold-Press Oil Expeller with Filter Press",
                amount=Decimal("68000.00"),
                is_essential=True,
            )
            FinancialExpense.objects.create(
                financial_plan=fp,
                expense_type="STARTUP",
                category="Packaging & Scales",
                description="Digital platform scale, band sealer, and food-grade storage drums",
                amount=Decimal("10000.00"),
                is_essential=True,
            )
            FinancialExpense.objects.create(
                financial_plan=fp,
                expense_type="VARIABLE_MONTHLY",
                category="Raw Oilseeds",
                description="18 Quintals local Sarson (Mustard Seed) from Samrala Mandi",
                amount=Decimal("62000.00"),
                is_essential=True,
            )

        MarketObservation.objects.get_or_create(
            user=user,
            subject_name="Samrala Block Retail Mustard Oil & Khal Check",
            defaults={
                "business_plan": bp,
                "state": "Punjab",
                "district": "Ludhiana",
                "village_or_town": "Samrala Block",
                "business_category": "FOOD_PROCESSING",
                "observation_type": "PRICING",
                "observed_price_or_metric": "₹170–₹185/litre unrefined oil; ₹34/kg mustard oil-cake",
                "competitor_count": 2,
                "demand_level": "HIGH",
                "supplier_availability": "BLOCK_TOWN",
                "details": "Only 2 old expellers in a 9 km radius; dairy owners currently travel 14 km to buy pure mustard khal.",
                "data_source_type": "USER_PROVIDED",
            },
        )

        snap = {
            "metrics": calculate_financial_projections(fp),
            "scenarios": build_scenario_comparisons(fp),
            "formulas": get_formula_explanations(),
        }
        Report.objects.get_or_create(
            user=user,
            title="Samrala Cold-Press Oil Mill — PMEGP / MUDRA Appraisal Dossier",
            defaults={
                "business_plan": bp,
                "financial_plan": fp,
                "report_type": "BANK_LOAN_PROPOSAL",
                "executive_summary": (
                    "Proposal for setting up a 3 HP Cold-Press Mustard Oil and Cattle Feed Cake unit in Samrala Block, "
                    "Ludhiana (Punjab). Total startup investment is ₹1,18,000 backed by ₹85,000 own promoter equity and "
                    "₹60,000 PMMY-Kishore / PMEGP credit linkage. Expected monthly operating profit (EBITDA) is ₹30,750 "
                    "with a 27.03% operating margin and a 3.8-month startup payback period."
                ),
                "snapshot_data": json.dumps(snap, default=str),
            },
        )
        self.stdout.write(
            self.style.SUCCESS("Seeded demo entrepreneur user 'demo_kisan' (password: RuralPass@2026) with sample plans.")
        )
