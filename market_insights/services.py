'''
Hyper-Local Market Research & Official Government Funding Schemes Service.

Strict Data Honesty Policy:
- Distinguishes between User-Provided Field Observations, General Sector Guidance,
  and Unverified Field Estimates.
- Never fabricates real-time mandi prices or claims geographic personalization
  is a substitute for primary local field research.
- Provides documented central government schemes with official portal URLs and
  explicit non-guarantee disclaimers.
'''
from datetime import date
from decimal import Decimal
from market_insights.models import FundingScheme


DEFAULT_FUNDING_SCHEMES = [
    {
        "name": "Prime Minister's Employment Generation Programme (PMEGP)",
        "short_code": "PMEGP",
        "ministry_or_agency": "Ministry of MSME — Khadi and Village Industries Commission (KVIC)",
        "scheme_type": "CREDIT_LINKED_SUBSIDY",
        "applicable_categories": "FOOD_PROCESSING,DAIRY_LIVESTOCK,HANDICRAFTS_TEXTILE,RURAL_SERVICES,SMALL_MANUFACTURING,RENEWABLE_AGRITECH",
        "min_investment": Decimal("50000.00"),
        "max_funding_amount": Decimal("5000000.00"),
        "eligibility_criteria": (
            "• Any individual aged 18+ years starting a new micro-enterprise in manufacturing or services.\n"
            "• Minimum VIII standard pass required for projects costing above ₹10 Lakh in manufacturing or ₹5 Lakh in service sector.\n"
            "• Self-Help Groups (SHGs), Charitable Trusts, and Production Co-operative Societies are also eligible.\n"
            "• Only new projects are eligible (existing units or units that already availed government subsidy are excluded)."
        ),
        "potential_benefits": (
            "• Margin Money Subsidy in Rural Areas: 25% of project cost for General Category, and 35% for Special Category (SC/ST/OBC/Minorities/Women/Ex-Servicemen/Physically Challenged).\n"
            "• Own Contribution: 10% for General Category and 5% for Special Category.\n"
            "• Maximum eligible project cost: Up to ₹50 Lakh for Manufacturing units and up to ₹20 Lakh for Service/Business units."
        ),
        "required_documents": (
            "1. Aadhaar Card & PAN Card\n"
            "2. Caste / Special Category Certificate (if applicable)\n"
            "3. Rural Area Certificate from Tehsildar / Gram Panchayat\n"
            "4. Detailed Project Report (DPR) with machinery quotations & financial projections\n"
            "5. Highest Educational / Skill Qualification Certificate\n"
            "6. Passport-size photographs and bank passbook copy"
        ),
        "application_process": (
            "1. Submit online application exclusively on the KVIC PMEGP e-Portal.\n"
            "2. Select sponsoring agency (KVIC / KVIB / DIC) and preferred financing bank branch.\n"
            "3. Upload project report, rural certificate, and identity documents.\n"
            "4. After bank credit appraisal and sanction, complete mandatory Entrepreneurship Development Programme (EDP) training."
        ),
        "official_source_url": "https://www.kviconline.gov.in/pmegpeportal/",
        "last_verification_date": date(2026, 4, 1),
    },
    {
        "name": "Pradhan Mantri MUDRA Yojana (PMMY — Shishu, Kishore & Tarun)",
        "short_code": "PMMY-MUDRA",
        "ministry_or_agency": "Ministry of Finance / Micro Units Development & Refinance Agency Ltd.",
        "scheme_type": "COLLATERAL_FREE_LOAN",
        "applicable_categories": "ALL",
        "min_investment": Decimal("10000.00"),
        "max_funding_amount": Decimal("2000000.00"),
        "eligibility_criteria": (
            "• Non-corporate, non-farm small/micro enterprises engaged in manufacturing, processing, trading, or services (including allied agricultural activities like dairy, poultry, beekeeping, and agri-clinics).\n"
            "• Applicant should not be a defaulter to any bank or financial institution."
        ),
        "potential_benefits": (
            "• Collateral-free institutional credit under three tiers:\n"
            "  - Shishu: Loans up to ₹50,000 for micro startups.\n"
            "  - Kishore: Loans from ₹50,001 to ₹5,00,000 for expansion/equipment.\n"
            "  - Tarun / Tarun Plus: Loans up to ₹10,00,000 (and up to ₹20,00,000 for timely repayers).\n"
            "• Working capital via MUDRA Card (RuPay debit card) and term loan for machinery."
        ),
        "required_documents": (
            "1. Identity & Address Proof (Aadhaar, Voter ID, PAN)\n"
            "2. Udyam Registration Certificate\n"
            "3. Quotations for machinery / equipment and raw material suppliers\n"
            "4. Last 6 months bank statement\n"
            "5. Business place proof (ownership or rent agreement)"
        ),
        "application_process": (
            "1. Prepare a concise Financial Plan & Break-Even summary using this portal.\n"
            "2. Apply online via the JanSamarth Portal or visit your nearest Public/Private Sector Bank, Regional Rural Bank (RRB), or Small Finance Bank.\n"
            "3. Submit machinery quotations and cash-flow projections for branch appraisal."
        ),
        "official_source_url": "https://www.mudra.org.in/",
        "last_verification_date": date(2026, 4, 1),
    },
    {
        "name": "PM Formalisation of Micro Food Processing Enterprises (PMFME)",
        "short_code": "PMFME",
        "ministry_or_agency": "Ministry of Food Processing Industries (MoFPI)",
        "scheme_type": "FOOD_PROCESSING_UPGRADE",
        "applicable_categories": "FOOD_PROCESSING,DAIRY_LIVESTOCK,AGRI_ALLIED",
        "min_investment": Decimal("25000.00"),
        "max_funding_amount": Decimal("3000000.00"),
        "eligibility_criteria": (
            "• Existing or new micro food processing units (Proprietorship, Partnership, FPOs, SHGs, NGOs, Cooperatives).\n"
            "• Preference for One District One Product (ODOP) food processing units, though non-ODOP upgrades are also supported.\n"
            "• Minimum 10% beneficiary contribution required."
        ),
        "potential_benefits": (
            "• Credit-linked capital subsidy of 35% of the eligible project cost, up to a maximum ceiling of ₹10.00 Lakh per unit.\n"
            "• Seed Capital of up to ₹40,000 per SHG member engaged in food processing for working capital and small tools.\n"
            "• Handholding support for DPR preparation, FSSAI registration, and packaging/branding training."
        ),
        "required_documents": (
            "1. Aadhaar Card & PAN Card of Proprietor/Promoters\n"
            "2. Proof of address & bank account statement (last 6 months)\n"
            "3. Quotations for food processing plant & machinery\n"
            "4. Udyam & FSSAI Registration (or application acknowledgement)\n"
            "5. Electricity bill / land or shed lease document"
        ),
        "application_process": (
            "1. Register on the official PMFME portal (pmfme.mofpi.gov.in).\n"
            "2. Connect with the District Resource Person (DRP) appointed by the State Nodal Agency for free DPR assistance.\n"
            "3. Submit online application for District Level Committee recommendation and bank loan sanction."
        ),
        "official_source_url": "https://pmfme.mofpi.gov.in/",
        "last_verification_date": date(2026, 4, 1),
    },
    {
        "name": "Deendayal Antyodaya Yojana — National Rural Livelihoods Mission (DAY-NRLM / SVEP)",
        "short_code": "DAY-NRLM",
        "ministry_or_agency": "Ministry of Rural Development (MoRD) & State Rural Livelihood Missions",
        "scheme_type": "SHG_LIVELIHOOD",
        "applicable_categories": "ALL",
        "min_investment": Decimal("5000.00"),
        "max_funding_amount": Decimal("500000.00"),
        "eligibility_criteria": (
            "• Women members of active Self-Help Groups (SHGs) or their family members under the Start-up Village Entrepreneurship Programme (SVEP).\n"
            "• SHG must follow 'Panchasutra' (regular meetings, regular savings, internal lending, timely repayment, and updated books of accounts)."
        ),
        "potential_benefits": (
            "• Revolving Fund (RF) of ₹20,000–₹30,000 per eligible SHG and Community Investment Fund (CIF) up to ₹2.50 Lakh per federation.\n"
            "• Collateral-free SHG-Bank Linkage loans with interest subvention for prompt repayment.\n"
            "• Mentorship through trained Community Resource Persons — Enterprise Promotion (CRP-EP)."
        ),
        "required_documents": (
            "1. SHG Membership & Resolution Copy from Village Organization (VO)\n"
            "2. Aadhaar Card & Individual Bank Account Passbook\n"
            "3. Micro-Enterprise Business Plan prepared with CRP-EP\n"
            "4. SHG Grading / Audit Record"
        ),
        "application_process": (
            "1. Present your business & financial plan at your weekly/monthly SHG meeting.\n"
            "2. Include the enterprise request in the Micro Credit Plan (MCP) forwarded to the Village Organization (VO) / Cluster Level Federation (CLF).\n"
            "3. Avail CIF seed loan or SHG-Bank linkage credit through the block NRLM office."
        ),
        "official_source_url": "https://aajeevika.gov.in/",
        "last_verification_date": date(2026, 4, 1),
    },
    {
        "name": "Stand-Up India Scheme for SC/ST and Women Entrepreneurs",
        "short_code": "STANDUP-INDIA",
        "ministry_or_agency": "Department of Financial Services (DFS), Ministry of Finance",
        "scheme_type": "SC_ST_WOMEN_TERM_LOAN",
        "applicable_categories": "FOOD_PROCESSING,DAIRY_LIVESTOCK,RURAL_SERVICES,RENEWABLE_AGRITECH,SMALL_MANUFACTURING,AGRI_ALLIED",
        "min_investment": Decimal("1000000.00"),
        "max_funding_amount": Decimal("10000000.00"),
        "eligibility_criteria": (
            "• SC/ST and/or Women entrepreneurs aged 18+ years setting up a greenfield (first-time) enterprise in manufacturing, services, agri-allied activities, or trading.\n"
            "• In case of non-individual enterprises, at least 51% of shareholding and controlling stake must be held by an SC/ST or Woman entrepreneur."
        ),
        "potential_benefits": (
            "• Composite loan (inclusive of term loan and working capital) between ₹10 Lakh and ₹100 Lakh (₹1 Crore).\n"
            "• Covers up to 85% of project cost; borrower contribution can be reduced to 10% if converged with central/state subsidy schemes.\n"
            "• Repayment tenure up to 7 years with a maximum moratorium period of 18 months."
        ),
        "required_documents": (
            "1. Identity, Address & PAN Proof\n"
            "2. SC/ST Certificate (where applicable)\n"
            "3. Business Incorporation / Udyam Registration & Project Report\n"
            "4. Land/Shed Lease or Title Documents & Pollution/Local NOC\n"
            "5. Promoter Net Worth & Last 3 Years ITR (if available)"
        ),
        "application_process": (
            "1. Apply online via the Stand-Up Mitra portal (standupmitra.in).\n"
            "2. Opt for handholding support from Lead District Manager (LDM), NABARD, or SIDBI if needed.\n"
            "3. Track loan application appraisal across scheduled commercial bank branches."
        ),
        "official_source_url": "https://www.standupmitra.in/",
        "last_verification_date": date(2026, 4, 1),
    },
    {
        "name": "Agriculture Infrastructure Fund (AIF) — Post-Harvest & Farm-Gate Units",
        "short_code": "AGRI-INFRA",
        "ministry_or_agency": "Ministry of Agriculture & Farmers Welfare",
        "scheme_type": "NABARD_RURAL_INNOVATION",
        "applicable_categories": "AGRI_ALLIED,FOOD_PROCESSING,RENEWABLE_AGRITECH,DAIRY_LIVESTOCK",
        "min_investment": Decimal("50000.00"),
        "max_funding_amount": Decimal("20000000.00"),
        "eligibility_criteria": (
            "• Farmers, Agri-Entrepreneurs, Start-ups, FPOs, SHGs, PACS, and Joint Liability Groups (JLGs).\n"
            "• Eligible projects include primary processing centres, custom hiring centres, solar cold storage, sorting/grading/assaying units, warehouses, and organic input production."
        ),
        "potential_benefits": (
            "• 3% per annum interest subvention on term loans up to ₹2 Crore for a maximum period of 7 years.\n"
            "• Credit Guarantee coverage under CGTMSE for loans up to ₹2 Crore (fee borne by Government).\n"
            "• Can be dovetailed with PMFME or state capital subsidies."
        ),
        "required_documents": (
            "1. Detailed Project Report (DPR) & Machinery Quotations\n"
            "2. Aadhaar, PAN & Land/Premises Ownership or Lease Proof\n"
            "3. Bank Account Statements (6 months)\n"
            "4. Udyam / FPO / SHG Registration Proof"
        ),
        "application_process": (
            "1. Register as a beneficiary on agriinfra.dac.gov.in.\n"
            "2. Submit project cost details and select preferred lending institution.\n"
            "3. After Central/State PMU verification of project eligibility, the lending bank appraises and sanctions the subvented loan."
        ),
        "official_source_url": "https://agriinfra.dac.gov.in/",
        "last_verification_date": date(2026, 4, 1),
    },
]


def ensure_default_schemes_seeded():
    '''Ensures the database contains the verified default funding schemes.'''
    for sdata in DEFAULT_FUNDING_SCHEMES:
        FundingScheme.objects.get_or_create(
            name=sdata["name"],
            defaults=sdata,
        )


def get_regional_category_guidance(category_key):
    '''
    Returns general, non-statistical field research checklists by category.
    Explicitly labelled as General Sector Guidance so users know what to verify locally.
    '''
    guidance_map = {
        "FOOD_PROCESSING": {
            "label": "General Sector Guidance (Verify Locally in Your Block Mandi)",
            "seasonal_factors": "Raw grain/oilseed prices are typically 15–25% lower during the 45-day post-harvest arrival window. Plan working capital to stock raw inputs during harvest.",
            "supplier_tips": "Compare farm-gate procurement rates from local farmers/FPOs against APMC mandi commission agent rates.",
            "pricing_checklist": "Check retail prices of loose vs. packed 1kg/1L brands at 5 village kirana stores and 1 block town wholesale market.",
        },
        "AGRI_ALLIED": {
            "label": "General Sector Guidance (Verify Crop Calendar with Local KVK)",
            "seasonal_factors": "Demand for custom hiring and seedlings peaks sharply 2–3 weeks before Kharif (June–July) and Rabi (Oct–Nov) sowing.",
            "supplier_tips": "Verify spare parts availability and authorized mechanic support within 20 km before buying machinery.",
            "pricing_checklist": "Record hourly tractor/weeder rental rates and seedling per-tray prices in 3 neighbouring villages.",
        },
        "DAIRY_LIVESTOCK": {
            "label": "General Sector Guidance (Verify Local Milk Route & Fodder Supply)",
            "seasonal_factors": "Green fodder scarcity and summer heat (May–July) reduce milk yield by 15–20% while increasing paneer/curd demand for weddings and dhabas.",
            "supplier_tips": "Lock in dry fodder (turi/straw) and mustard oil-cake suppliers right after Rabi harvest.",
            "pricing_checklist": "Check cooperative dairy fat/SNF procurement chart vs. private halwai/dhaba bulk buying rates.",
        },
        "RURAL_RETAIL": {
            "label": "General Sector Guidance (Verify Footfall & Wholesale Credit Terms)",
            "seasonal_factors": "Rural household cash flow peaks post-harvest and around major festivals; keep credit exposure strictly capped during mid-season months.",
            "supplier_tips": "Compare distributor delivery margins vs. self-pickup from district wholesale mandi.",
            "pricing_checklist": "List the top 25 daily-use items where villagers currently travel to the block town due to lack of local stock.",
        },
    }
    return guidance_map.get(
        category_key,
        {
            "label": "General Sector Guidance (Requires Primary Local Verification)",
            "seasonal_factors": "Rural demand fluctuates with agricultural harvest cash flows, wedding seasons, and monsoon road connectivity.",
            "supplier_tips": "Identify at least two independent raw material or spare-part suppliers at the block/district level to avoid single-supplier dependency.",
            "pricing_checklist": "Interview 10 prospective local customers and 3 existing shopkeepers before finalizing your price list.",
        },
    )


def build_regional_market_synthesis(observations, category_key=None):
    '''
    Synthesizes user-recorded MarketObservation records into actionable insights
    while strictly labelling the evidence basis.
    '''
    obs_list = list(observations)
    total = len(obs_list)
    if total == 0:
        return {
            "has_user_evidence": False,
            "evidence_label": "No User Field Observations Recorded Yet — Showing General Sector Guidance Only",
            "summary": "Log local competitor counts, mandi/retail prices, and supplier locations below to generate evidence-backed hyper-local recommendations.",
            "recommendations": [
                "Visit 3–5 local shops or weekly haats in your block to record current selling prices.",
                "Identify how many direct competitors operate within a 10 km radius of your village.",
                "Check whether raw materials can be sourced within the village/block or require district transport.",
            ],
        }

    high_demand = sum(1 for o in obs_list if o.demand_level == "HIGH")
    seasonal_demand = sum(1 for o in obs_list if o.demand_level == "SEASONAL")
    local_suppliers = sum(1 for o in obs_list if o.supplier_availability in ("LOCAL_VILLAGE", "BLOCK_TOWN"))
    comp_counts = [o.competitor_count for o in obs_list if o.competitor_count is not None]
    avg_competitors = round(sum(comp_counts) / len(comp_counts), 1) if comp_counts else None

    recs = []
    if high_demand > 0:
        recs.append(
            f"Based on your {high_demand} high-demand observation(s), prioritize quick setup and reliable inventory availability for those specific items/services."
        )
    if seasonal_demand > 0:
        recs.append(
            "Your field notes indicate seasonal demand spikes: pair your main product with an off-season secondary line or custom job-work service."
        )
    if local_suppliers == total:
        recs.append(
            "Strong Local Sourcing Advantage: All recorded inputs are available at village/block level, allowing lower working capital and transport outlays."
        )
    else:
        recs.append(
            "Some inputs require District HQ or outside sourcing: consolidate transport trips bi-weekly to protect operating margins."
        )
    if avg_competitors is not None:
        if avg_competitors <= 2:
            recs.append(
                f"Low Local Competition (avg {avg_competitors} competitors logged): Focus on doorstep awareness, clear pricing, and consistent hours."
            )
        else:
            recs.append(
                f"Active Competition (avg {avg_competitors} competitors logged): Differentiate through purity guarantee, smaller affordable pack sizes, or doorstep delivery."
            )

    return {
        "has_user_evidence": True,
        "evidence_label": f"Derived from {total} User-Recorded Field Observation(s) + General Sector Guidance",
        "total_observations": total,
        "avg_competitors": avg_competitors,
        "recommendations": recs,
    }
