'''
Provider-independent AI Business Advisory Service Layer with a clearly-labelled,
deterministic Rule-Based Fallback Engine for Rural Micro-Entrepreneurs.

Security & Honesty Guarantees:
- Never invents real-time local market statistics or claims verified scheme sanction.
- Enforces per-user rate limiting on external AI provider requests.
- Handles AI timeouts, network failures, and malformed JSON gracefully by falling back
  to the deterministic Rule-Based Domain Engine.
- Treats all AI text as untrusted plain text (never raw HTML or executable code).
'''
import json
import logging
from decimal import Decimal, ROUND_HALF_UP
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)

# Domain knowledge base for rural micro-enterprises by category
RURAL_OPPORTUNITY_CATALOG = {
    "FOOD_PROCESSING": [
        {
            "name": "Mini Mustard / Groundnut Cold-Press Oil Expeller & Oil-Cake Unit",
            "base_cost": Decimal("115000.00"),
            "min_budget": Decimal("45000.00"),
            "setup": "3 HP single-phase/three-phase cold-press expeller, filter press, food-grade storage drums, weighing scale, FSSAI basic registration, and 200 sq.ft. ventilated shed.",
            "customers": "Village households, local sweet shops (halwais), block kirana retailers, and dairy farmers (who buy oil-cake/khal as cattle feed).",
            "marketing": "Offer 'job-work' crushing (custom milling for farmers bringing their own oilseeds) alongside branded 1L/5L pouches sold at weekly haats and village kirana stores.",
            "risks": "Seasonal oilseed price volatility during post-harvest months; adulteration competition from cheap refined oils.",
            "mitigation": "Procure oilseeds directly from local farmers at harvest; generate dual revenue by selling nutrient-rich oil-cake (khal) to local dairy owners for immediate cash flow.",
            "steps": "1. Secure Udyam & FSSAI Basic Registration (₹100 fee).\n2. Lease or prepare a 200 sq.ft. pucca room with reliable power.\n3. Procure mini expeller with 1-year motor warranty.\n4. Launch custom-crushing service for village farmers first to build trust.\n5. Package filtered oil in 500ml, 1L, and 5L food-grade jars.",
        },
        {
            "name": "Multi-Grain & Millet (Shree Anna) Flour, Dalia & Roasted Snack Unit",
            "base_cost": Decimal("85000.00"),
            "min_budget": Decimal("30000.00"),
            "setup": "Pulverizer/atta chakki (stoneless or emery stone), destoner, roaster drum, heat sealer, digital scale, and FSSAI registration.",
            "customers": "Health-conscious town families, rural households, anganwadi/school nutrition suppliers, and local grocery stores.",
            "marketing": "Supply freshly ground bajra, jowar, ragi, and besan blends in 1 kg moisture-proof pouches; partner with block-level self-help group (SHG) outlets.",
            "risks": "Shorter shelf life of whole-grain millet flour (30–45 days) and moisture spoilage during monsoon.",
            "mitigation": "Mill in small weekly batches against confirmed retailer orders and dry grains thoroughly before grinding; use food-grade laminated stand-up pouches.",
            "steps": "1. Identify local availability of wheat, bajra, jowar, or chana from nearby mandis.\n2. Install compact pulverizer and sealing machine.\n3. Obtain FSSAI registration and print compliant nutrition/date labels.\n4. Distribute sample 250g packs at block markets and doctors' clinics.\n5. Establish weekly replenishment routes with 10–15 kirana shops.",
        },
        {
            "name": "Commercial Spice Grinding, Haldi-Mirch-Dhaniya & Pickle Unit",
            "base_cost": Decimal("65000.00"),
            "min_budget": Decimal("20000.00"),
            "setup": "SS spice pulverizer, solar/tray dryer for chillies and turmeric, weighing scale, band sealer, and hygienic drying space.",
            "customers": "Rural & semi-urban households, roadside dhabas, marriage caterers, and weekly haat traders.",
            "marketing": "Position as '100% pure, zero-filler village spices' in ₹10, ₹20, and ₹50 sachets as well as 500g family packs; offer bulk rates to local caterers.",
            "risks": "Working capital lock-up in raw spice inventory; dust/eye irritation for operators during grinding.",
            "mitigation": "Use covered cyclone-collector grinders with operator masks; buy raw turmeric/chilli during harvest peak in phased lots.",
            "steps": "1. Register under Udyam and FSSAI Basic category.\n2. Set up solar drying racks to keep moisture below 10%.\n3. Install compact stainless-steel hammer mill.\n4. Introduce ₹10/₹20 hanging strip sachets for village kirana shops.\n5. Expand into seasonal mango/lemon/chilli pickles for higher margins.",
        },
    ],
    "AGRI_ALLIED": [
        {
            "name": "Custom Hiring Centre (Power Weeder, Sprayer, Reaper & chaff cutter)",
            "base_cost": Decimal("140000.00"),
            "min_budget": Decimal("40000.00"),
            "setup": "Mini power tiller/weeder, battery/engine knapsack sprayers, brush cutter, reaper attachment, and basic mechanic toolkit.",
            "customers": "Small and marginal farmers (1–4 acres) who cannot afford to buy individual farm machinery.",
            "marketing": "Charge transparent per-acre or per-hour rental rates; coordinate bookings via village WhatsApp groups, panchayat noticeboards, and FPOs.",
            "risks": "Highly seasonal demand clustered around sowing and harvesting windows; equipment breakdown during peak week.",
            "mitigation": "Keep spare belts, spark plugs, and filters in stock; offer off-season fodder cutting and orchard spraying to maintain year-round cash flow.",
            "steps": "1. Survey 3–4 neighbouring villages to list crop calendar gaps.\n2. Procure 2–3 high-demand implements suited to local soil.\n3. Fix standard hourly/acre rates including operator fuel.\n4. Train one backup operator for peak harvest weeks.\n5. Maintain a logbook of machine hours and preventive servicing.",
        },
        {
            "name": "Commercial Vegetable & Fruit Seedling Nursery (Shade-Net Unit)",
            "base_cost": Decimal("55000.00"),
            "min_budget": Decimal("20000.00"),
            "setup": "50% UV-stabilized shade net structure (1,000 sq.ft.), pro-trays, cocopeat, vermicompost, mist sprayer, and certified hybrid seeds.",
            "customers": "Local vegetable growers, kitchen gardeners, orchard farmers, and panchayat plantation drives.",
            "marketing": "Take advance booking 30 days before transplanting season for tomato, chilli, cauliflower, onion, and papaya seedlings.",
            "risks": "Damping-off fungal disease or extreme heatwave mortality of tender seedlings.",
            "mitigation": "Use sterilized cocopeat media, treated hybrid seeds, and raised benches; collect 25% advance deposit on bulk farmer orders.",
            "steps": "1. Prepare well-drained plot with clean water access.\n2. Erect bamboo or GI-pipe shade-net house.\n3. Source certified disease-resistant seeds from agricultural university/KVK.\n4. Sow staggered batches in pro-trays every 10 days.\n5. Deliver hardened, pest-free seedlings at block farmer meetings.",
        },
        {
            "name": "Vermicompost, Bio-Fertilizer & Organic Input Production Unit",
            "base_cost": Decimal("38000.00"),
            "min_budget": Decimal("12000.00"),
            "setup": "8–12 HDPE vermi-beds (12x4x2 ft), Eisenia fetida earthworm culture, cow dung sourcing arrangement, sieve machine, and 5kg/40kg stitching bags.",
            "customers": "Orchard owners, vegetable farmers, nurseries, and semi-urban terrace gardeners.",
            "marketing": "Sell both bulk 40 kg bags to farmers and high-margin 2 kg / 5 kg retail packets to town nurseries; sell surplus earthworm culture to new units.",
            "risks": "Moisture desiccation in summer or ant/rodent attack on earthworm beds.",
            "mitigation": "Keep beds under tree shade or thatch roof, maintain 60% moisture via regular sprinkling, and create water channels/ash border around beds.",
            "steps": "1. Tie up with local dairy farms for regular cow dung supply.\n2. Pre-decompose dung for 15 days to eliminate excess heat.\n3. Install HDPE vermi-beds and introduce Eisenia fetida worms.\n4. Harvest first batch at 60–75 days, sieve, and pack in moisture-retentive bags.\n5. Register with KVK / organic farming groups for steady institutional buyers.",
        },
    ],
    "DAIRY_LIVESTOCK": [
        {
            "name": "Village Milk Collection, Cream Separation & Paneer/Ghee Value-Addition Unit",
            "base_cost": Decimal("95000.00"),
            "min_budget": Decimal("35000.00"),
            "setup": "Ultrasonic milk analyzer/lactometer, cream separator, stainless steel boiling vat, paneer press, deep freezer (300L), and FSSAI license.",
            "customers": "Local sweet shops, marriage caterers, dhabas, town households, and walk-in village buyers.",
            "marketing": "Convert surplus evening milk into fresh paneer, khoya, curd, and pure desi ghee which command 25–40% higher realization than raw liquid milk.",
            "risks": "Milk curdling during summer power outages; fluctuating fat/SNF quality from suppliers.",
            "mitigation": "Test every can for fat/SNF before payment; use insulated ice boxes and inverter backup for the deep freezer.",
            "steps": "1. Set up transparent fat/SNF-based pricing chart for 10–20 pouring farmers.\n2. Install cream separator, SS paneer press, and chest freezer.\n3. Obtain FSSAI registration and maintain daily hygiene logs.\n4. Secure regular supply contracts with 3–5 local dhabas and caterers.\n5. Utilize leftover whey water for cattle feed or kadhi base to eliminate waste.",
        },
        {
            "name": "Balanced Cattle & Poultry Feed Pellet / Mash Mixing Unit",
            "base_cost": Decimal("110000.00"),
            "min_budget": Decimal("40000.00"),
            "setup": "Feed grinder-cum-mixer (500 kg/hr), digital platform scale, mineral mixture blender, bag stitcher, and dry storage godown.",
            "customers": "Village dairy farmers, commercial poultry/goat rearers, and milk cooperative societies.",
            "marketing": "Formulate cost-effective balanced ration using local maize, wheat bran, mustard/cottonseed cake, and mineral mix at 10–15% lower cost than distant brands.",
            "risks": "Aflatoxin fungal contamination if grains are stored in damp conditions; credit sales recovery delays.",
            "mitigation": "Store bags on wooden pallets away from walls; link feed credit repayment with weekly milk payment cycles.",
            "steps": "1. Consult KVK/veterinary nutritionist for BIS-standard feed formula using local ingredients.\n2. Install hammer mill and ribbon mixer.\n3. Source maize, choker, de-oiled cake, and salt/mineral mix in bulk.\n4. Pack in 25 kg and 50 kg woven sacks with clear ingredient tags.\n5. Offer 5 kg trial packs to progressive dairy farmers in the block.",
        },
    ],
    "RURAL_RETAIL": [
        {
            "name": "Modern Rural Kirana, Agri-Input & Daily Essentials Micro-Mart",
            "base_cost": Decimal("80000.00"),
            "min_budget": Decimal("25000.00"),
            "setup": "Slotted angle display racks, digital weighing scale, UPI QR soundbox, ledger/billing book, and fast-moving household & farm consumables inventory.",
            "customers": "Village families, farm labourers, and neighbouring hamlet residents.",
            "marketing": "Bundle monthly household grocery kits with harvest-time settlement or discounted cash rates; stock high-turnover staples and basic veterinary/farm supplies.",
            "risks": "Excessive informal credit (udhaar) eroding working capital; dead stock of slow-moving urban brands.",
            "mitigation": "Cap credit per household, maintain strict weekly inventory rotation, and focus 80% of capital on top-30 fast-moving staples (oil, pulses, tea, soap, salt).",
            "steps": "1. Choose a central village crossroads or bus-stop location.\n2. Install clean shelving and transparent price display boards.\n3. Source wholesale stock from district mandi distributors.\n4. Set clear cash-discount policy to discourage long credit cycles.\n5. Add mobile recharge and utility bill collection for daily footfall.",
        },
        {
            "name": "Digital Seva / Common Service Centre (CSC), Banking Correspondent & Agri-Kiosk",
            "base_cost": Decimal("52000.00"),
            "min_budget": Decimal("20000.00"),
            "setup": "Laptop/desktop, multifunction laser printer/scanner, Aadhaar biometric device, lamination machine, UPS inverter backup, and broadband/4G hotspot.",
            "customers": "Villagers needing AePS cash withdrawal, PM-KISAN/crop insurance enrollment, land records (fard/khatauni), students, and pensioners.",
            "marketing": "Display official service rate chart in local language; conduct awareness camps with Gram Panchayat and SHG meetings.",
            "risks": "Server downtime or connectivity drops; cash-handling security risks for AePS micro-ATM.",
            "mitigation": "Maintain dual-SIM internet backup, insure cash-in-transit, and settle excess cash at the link bank branch daily.",
            "steps": "1. Apply for CSC ID or bank BC point and complete mandatory certification.\n2. Set up shop with seating, power backup, and biometric scanner.\n3. Display clear service list (certificates, insurance, banking, exam forms).\n4. Partner with local schools and farmers for seasonal form-filling drives.\n5. Add stationery, passport photo printing, and lamination for high-margin walk-in income.",
        },
    ],
    "HANDICRAFTS_TEXTILE": [
        {
            "name": "Commercial Tailoring, School Uniform & Readymade Garment Stitching Hub",
            "base_cost": Decimal("48000.00"),
            "min_budget": Decimal("15000.00"),
            "setup": "2–3 motorized sewing machines, interlock/overlock machine, cutting table, steam iron, and starter threads/lining stock.",
            "customers": "Local schools (uniforms), village women and men, boutique/wholesale contractors in district towns.",
            "marketing": "Secure annual school uniform stitching contracts before new academic sessions; offer alterations, blouse/suit stitching, and festive wear.",
            "risks": "Seasonal lean months between festival and school reopening periods.",
            "mitigation": "Produce cloth shopping bags, petticoats, aprons, and cushion covers from fabric remnants during off-peak weeks for local haats.",
            "steps": "1. Set up well-lit workshop with motorized lockstitch and interlock machines.\n2. Approach 2–3 local private/government schools for uniform sizing and supply.\n3. Train 1–2 local women helpers on piece-rate stitching.\n4. Maintain strict delivery date tokens to build local reputation.\n5. Use leftover fabric scraps to stitch reusable cloth bags for kirana stores.",
        },
        {
            "name": "Artisanal Handloom, Phulkari / Embroidery & Eco-Jute Bag Unit",
            "base_cost": Decimal("42000.00"),
            "min_budget": Decimal("15000.00"),
            "setup": "Heavy-duty jute/canvas stitching machine, embroidery frames, block-printing kit, raw cotton/jute fabric rolls, and branding tags.",
            "customers": "Town retail boutiques, wedding gift buyers, corporate/NGO event organizers, and melas/exhibitions.",
            "marketing": "Register for Artisan Card (Pehchan) to access government Saras/Khadi exhibitions; supply custom-printed jute conference and wedding bags.",
            "risks": "Long payment cycles on exhibition/consignment orders; design stagnation.",
            "mitigation": "Focus 60% capacity on utilitarian jute/canvas bags with 50% advance payment, and 40% on high-margin artisanal dupattas/decor.",
            "steps": "1. Source raw jute/cotton canvas in bulk from wholesale textile market.\n2. Standardize 4 fast-selling bag sizes (lunch bag, grocery tote, wedding gift bag, file folder).\n3. Apply for Development Commissioner (Handicrafts) Pehchan Artisan ID.\n4. Pitch custom-printed bags to local sweet shops, jewellers, and schools.\n5. Showcase embroidered apparel at district Saras Melas and SHG exhibitions.",
        },
    ],
    "RURAL_SERVICES": [
        {
            "name": "Two-Wheeler, E-Rickshaw, Pump-Set & Tractor Electrical Repair Workshop",
            "base_cost": Decimal("68000.00"),
            "min_budget": Decimal("22000.00"),
            "setup": "Air compressor, pneumatic wrench, battery charger/tester, welding/soldering kit, spanner & socket set, puncture kit, and fast-moving spares (tubes, cables, brake shoes, engine oil).",
            "customers": "Village commuters, e-rickshaw operators, dairy milkmen, and farmers with diesel/electric pump sets.",
            "marketing": "Offer roadside breakdown call-out support within 5 km and fixed-price periodic servicing packages.",
            "risks": "Working capital tied up in slow-moving spare parts.",
            "mitigation": "Stock only fast-moving consumables (oils, filters, spark plugs, cables, bearings, tyres/tubes) and source rare spares on same-day order from block town.",
            "steps": "1. Rent a roadside spot near village entry, petrol pump, or mandi road.\n2. Install air compressor, ramp/stand, and battery charging bay.\n3. Stock genuine engine oils, brake cables, tubes, and e-rickshaw controller spares.\n4. Offer ₹99 quick-checkup camp to build initial customer base.\n5. Add motor-rewinding or pump-set repair for irrigation season demand.",
        },
        {
            "name": "Rural Tent, Sound System, Solar Lighting & Event Catering Equipment Rental",
            "base_cost": Decimal("125000.00"),
            "min_budget": Decimal("45000.00"),
            "setup": "Waterproof shamiana/pandal fabric, bamboo/iron pipes, 100 plastic chairs, folding tables, commercial cooking utensils (patilas/bhattis), and PA sound/LED lighting set.",
            "customers": "Village families (marriages, family functions), Gram Panchayat events, religious gatherings, and school sports days.",
            "marketing": "Create 3 transparent package tiers (Small Bhog/Meeting, Medium Function, Full Wedding Package) and partner with local halwais/caterers.",
            "risks": "Damage or loss of rented crockery/chairs; heavy seasonal clustering around marriage auspicious dates.",
            "mitigation": "Collect refundable security deposit and count inventory at dispatch/return; rent out chairs, coolers, and fans individually during summer.",
            "steps": "1. Purchase durable chairs, steel tables, commercial burners, and waterproof pandal sheets.\n2. Partner with 3–4 popular village halwais for mutual referrals.\n3. Print rate cards and booking receipt books with clear damage clauses.\n4. Maintain clean, freshly washed tent fabric to stand out from competitors.\n5. Reinvest peak wedding-season profits into silent generator or cooler rentals.",
        },
    ],
    "RENEWABLE_AGRITECH": [
        {
            "name": "Solar Dryer & Micro Cold-Room Aggregation Hub for Perishables",
            "base_cost": Decimal("145000.00"),
            "min_budget": Decimal("45000.00"),
            "setup": "Polycarbonate solar tunnel/cabinet dryer (100 kg capacity), moisture meter, vacuum/heat sealer, plastic crates, and insulated storage room.",
            "customers": "Vegetable/fruit farmers, FPOs, spice processors, and urban wholesale buyers of dehydrated fenugreek (kasuri methi), ginger, garlic, tomato, and amla.",
            "marketing": "Buy glut-season vegetables at low mandi prices and convert them into shelf-stable dehydrated flakes/powders with 9-month shelf life.",
            "risks": "Cloudy/monsoon weather slowing solar drying cycles.",
            "mitigation": "Equip dryer with auxiliary electric/biomass backup heater for cloudy days and schedule high-volume drying during sunny post-winter months.",
            "steps": "1. Identify local crops facing seasonal price crashes (tomato, methi, onion, ginger, turmeric).\n2. Install food-grade polycarbonate solar dryer with UV protection.\n3. Blanch and slice produce uniformly for consistent drying.\n4. Seal dehydrated produce in moisture-barrier pouches.\n5. Sell to spice blenders, hotels, and institutional caterers.",
        },
        {
            "name": "Solar Panel, Inverter Battery & Agricultural Solar Pump Maintenance Service",
            "base_cost": Decimal("35000.00"),
            "min_budget": Decimal("12000.00"),
            "setup": "Digital clamp meter, hydrometer, solar irradiance/panel tester, insulated electrician toolkit, telescopic panel-washing kit, and distilled water/terminal spares.",
            "customers": "Farmers with PM-KUSUM solar pumps, rural homes with inverter batteries, schools, and solar streetlights.",
            "marketing": "Offer Annual Maintenance Contracts (AMC) for solar pump controllers, panel cleaning, and inverter battery topping/desulfation.",
            "risks": "Electrical safety hazards when working on high-voltage DC solar strings.",
            "mitigation": "Use rated DC circuit breakers, insulated gloves, and follow manufacturer lockout procedures strictly.",
            "steps": "1. Complete short-term Suryamitra / KVK / ITI solar technician training.\n2. Map all solar irrigation pumps and inverter users in a 15 km radius.\n3. Offer quarterly panel cleaning + earthing/controller check packages.\n4. Stock distilled water, DC MC4 connectors, fuses, and surge arrestors.\n5. Partner with district solar dealers as their authorized local service point.",
        },
    ],
    "SMALL_MANUFACTURING": [
        {
            "name": "Biodegradable Areca / Sal Leaf & Heavy-GSM Paper Plate/Dona Manufacturing Unit",
            "base_cost": Decimal("72000.00"),
            "min_budget": Decimal("25000.00"),
            "setup": "Double-die hydraulic or crank paper dona/plate machine, raw silver/kraft paper rolls, die moulds (6-inch, 8-inch, 12-inch), and bundling wrapper.",
            "customers": "Sweet shops, street food vendors, marriage caterers, temples/gurudwaras (langar), and wholesale disposable dealers.",
            "marketing": "Supply directly to langar committees, dhabas, and block wholesalers in 100-piece shrink packs; capitalize on single-use plastic bans.",
            "risks": "Raw paper roll price fluctuations and thin margins on generic lightweight donas.",
            "mitigation": "Produce thicker 100–120 GSM wrinkled plates and compartment thalis which command better margins and lower competition.",
            "steps": "1. Install low-noise hydraulic double-die machine on single-phase domestic/commercial power.\n2. Source pre-cut paper circles or rolls from wholesale paper mills.\n3. Tie up with 5–10 local sweet shops, chaat vendors, and caterers.\n4. Collect paper trimmings/scrap for resale to recycling vendors.\n5. Scale output ahead of festival and wedding seasons.",
        },
        {
            "name": "Liquid Detergent, Dishwash Gel, Phenyl & Floor Cleaner Formulation Unit",
            "base_cost": Decimal("38000.00"),
            "min_budget": Decimal("12000.00"),
            "setup": "HDPE mixing barrels (200L), mechanical stirrer, pH strips, hydrometer, filling nozzle, and PET bottles/5L cans with printed labels.",
            "customers": "Village households, local schools, clinics, panchayat bhawans, dhabas, and rural kirana stores.",
            "marketing": "Offer 'refill-your-own-bottle' at 30% discount to village families, and supply 5-litre institutional cans to schools, hospitals, and dhabas.",
            "risks": "Improper chemical neutralization causing skin irritation or phase separation.",
            "mitigation": "Strictly test pH (neutral 6.5–7.5 for dishwash/liquid soap) on every batch using pH strips and standard BIS-aligned formulas.",
            "steps": "1. Obtain Udyam registration and source raw materials (SLES, acid slurry, caustic soda, pine oil) from verified chemical wholesalers.\n2. Set up well-ventilated mixing room away from children and food storage.\n3. Test batch quality and pH stability over 7 days.\n4. Launch 1L retail bottles and 5L bulk cans for local institutions.\n5. Appoint महिला SHG members as village-level retail distributors on 15% margin.",
        },
    ],
}


def check_and_increment_ai_rate_limit(user_id):
    '''
    Enforces per-user hourly rate limiting on external AI advisory calls.
    Returns (allowed: bool, remaining: int).
    '''
    limit = getattr(settings, "AI_RATE_LIMIT_PER_HOUR", 15)
    cache_key = f"ai_rate_limit_user_{user_id}"
    current = cache.get(cache_key, 0)
    if current >= limit:
        return False, 0
    cache.set(cache_key, current + 1, timeout=3600)
    return True, max(0, limit - (current + 1))


def _determine_risk_level(investment_budget, constraints_text):
    constraints_lower = (constraints_text or "").lower()
    high_risk_keywords = ["debt", "flood", "no power", "no electricity", "perishable", "dispute", "shortage"]
    risk_hits = sum(1 for kw in high_risk_keywords if kw in constraints_lower)
    if investment_budget > Decimal("300000.00") or risk_hits >= 2:
        return "HIGH"
    if investment_budget < Decimal("60000.00") and risk_hits == 0:
        return "LOW"
    return "MODERATE"


def generate_rule_based_recommendations(plan_data):
    '''
    Deterministic, provider-independent rule-based advisory engine.
    Always produces 3 structured, realistic, budget-adjusted recommendations
    explicitly labelled as Rule-Based Fallback guidance.
    '''
    category = plan_data.get("business_category", "FOOD_PROCESSING")
    budget = Decimal(str(plan_data.get("investment_budget") or "50000.00"))
    state = plan_data.get("state", "Punjab")
    district = plan_data.get("district", "Local District")
    village = plan_data.get("village_or_town", "Local Village")
    skills = plan_data.get("existing_skills", "")
    resources = plan_data.get("existing_resources", "")
    target_customers = plan_data.get("target_customers", "Local households and traders")
    objectives = plan_data.get("business_objectives", "")
    constraints = plan_data.get("constraints", "")
    custom_idea = (plan_data.get("business_idea") or "").strip()

    catalog_items = list(RURAL_OPPORTUNITY_CATALOG.get(category, RURAL_OPPORTUNITY_CATALOG["FOOD_PROCESSING"]))
    # Add cross-category low-capital option if fewer than 3
    if len(catalog_items) < 3:
        catalog_items.append(RURAL_OPPORTUNITY_CATALOG["RURAL_RETAIL"][0])

    recommendations = []
    source_label = "Rule-Based Domain Engine (Offline Fallback — Non-Statistical Guidance)"

    for idx, item in enumerate(catalog_items[:3]):
        # Scale estimated startup cost realistically to fit within or near user's budget
        base_cost = item["base_cost"]
        min_budget = item["min_budget"]
        if budget < min_budget:
            est_cost = budget.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            scale_note = (
                f"Phased micro-scale start tailored to your ₹{budget:,.0f} budget "
                f"(standard full-scale setup is ~₹{base_cost:,.0f}; start with leased/compact equipment or SHG linkage)."
            )
            score = max(68, 82 - idx * 5)
        elif budget <= base_cost * Decimal("1.3"):
            est_cost = min(budget, base_cost).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            scale_note = f"Well-aligned with your available investment budget of ₹{budget:,.0f}."
            score = max(78, 92 - idx * 4)
        else:
            est_cost = base_cost.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            scale_note = (
                f"Your ₹{budget:,.0f} budget comfortably covers the ₹{base_cost:,.0f} setup cost "
                f"plus 3–4 months of working capital reserve."
            )
            score = max(80, 94 - idx * 4)

        opp_name = item["name"]
        if idx == 0 and custom_idea:
            opp_name = f"{custom_idea} ({item['name']})"

        suitability_reasons = (
            f"1. Geographic Context: Tailored for {village}, {district} ({state}) focusing on {target_customers}.\n"
            f"2. Capital Fit: {scale_note}\n"
            f"3. Skill & Resource Utilization: Leverages your stated skills ({skills[:120] or 'general entrepreneurship'}) "
            f"and resources ({resources[:120] or 'local workspace'}).\n"
            f"4. Objective Alignment: Supports your goal ({objectives[:120] or 'sustainable monthly household income'})."
        )

        mitigation = item["mitigation"]
        if constraints:
            mitigation += f"\n• Local Constraint Plan ({constraints[:90]}): Start with low fixed overheads, maintain a 3-month working capital buffer, and verify local buyer demand before expanding capacity."

        recommendations.append(
            {
                "opportunity_name": opp_name[:200],
                "suitability_score": score,
                "suitability_reasons": suitability_reasons,
                "initial_setup_requirements": item["setup"],
                "estimated_startup_cost": est_cost,
                "potential_customer_segments": f"{item['customers']} Primary target: {target_customers}.",
                "marketing_and_distribution": item["marketing"],
                "major_risks": item["risks"],
                "mitigation_measures": mitigation,
                "implementation_steps": item["steps"],
                "is_selected": idx == 0,
                "source_label": source_label,
            }
        )

    risk_level = _determine_risk_level(budget, constraints)
    return {
        "advisory_source": "RULE_BASED_FALLBACK",
        "risk_level": risk_level,
        "recommendations": recommendations,
        "fallback_reason": "Generated using deterministic Rule-Based Hyper-Local Advisory Engine (AI API disabled or not configured).",
    }


def call_external_ai_provider(plan_data, user_id=None):
    '''
    Calls an external OpenAI-compatible LLM endpoint if AI_PROVIDER_ENABLED=True
    and AI_API_KEY is configured. Safely validates JSON response and falls back
    to the rule-based engine on any error, timeout, or rate-limit exceedance.
    '''
    if not getattr(settings, "AI_PROVIDER_ENABLED", False) or not getattr(settings, "AI_API_KEY", ""):
        return generate_rule_based_recommendations(plan_data)

    if user_id is not None:
        allowed, _ = check_and_increment_ai_rate_limit(user_id)
        if not allowed:
            result = generate_rule_based_recommendations(plan_data)
            result["fallback_reason"] = "Hourly AI advisory rate limit reached; served via Rule-Based Fallback Engine."
            return result

    try:
        import requests
        prompt = (
            "You are a rural micro-enterprise business advisor in India. "
            "Do NOT invent real-time local statistics or guarantee government scheme approval. "
            "Return ONLY a JSON object with keys 'risk_level' (LOW/MODERATE/HIGH) and 'recommendations' "
            "(list of 3 objects with keys: opportunity_name, suitability_score, suitability_reasons, "
            "initial_setup_requirements, estimated_startup_cost, potential_customer_segments, "
            "marketing_and_distribution, major_risks, mitigation_measures, implementation_steps). "
            f"Context: {json.dumps(plan_data, default=str)}"
        )
        headers = {
            "Authorization": f"Bearer {settings.AI_API_KEY}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": getattr(settings, "AI_MODEL_NAME", "gpt-4o-mini"),
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
        }
        timeout = getattr(settings, "AI_TIMEOUT_SECONDS", 12)
        resp = requests.post(settings.AI_API_URL, headers=headers, json=payload, timeout=timeout)
        resp.raise_for_status()
        body = resp.json()
        content = body["choices"][0]["message"]["content"]
        parsed = json.loads(content)
        recs = parsed.get("recommendations", [])
        if not isinstance(recs, list) or len(recs) == 0:
            raise ValueError("Malformed AI response: missing recommendations list")

        cleaned_recs = []
        for idx, r in enumerate(recs[:3]):
            cleaned_recs.append(
                {
                    "opportunity_name": str(r.get("opportunity_name", "Rural Micro-Enterprise"))[:200],
                    "suitability_score": max(1, min(100, int(r.get("suitability_score", 80)))),
                    "suitability_reasons": str(r.get("suitability_reasons", "")),
                    "initial_setup_requirements": str(r.get("initial_setup_requirements", "")),
                    "estimated_startup_cost": Decimal(str(r.get("estimated_startup_cost", "50000.00"))).quantize(Decimal("0.01")),
                    "potential_customer_segments": str(r.get("potential_customer_segments", "")),
                    "marketing_and_distribution": str(r.get("marketing_and_distribution", "")),
                    "major_risks": str(r.get("major_risks", "")),
                    "mitigation_measures": str(r.get("mitigation_measures", "")),
                    "implementation_steps": str(r.get("implementation_steps", "")),
                    "is_selected": idx == 0,
                    "source_label": "AI-Assisted Advisory (External Provider — Verify Assumptions Locally)",
                }
            )
        risk = str(parsed.get("risk_level", "MODERATE")).upper()
        if risk not in ("LOW", "MODERATE", "HIGH"):
            risk = "MODERATE"
        return {
            "advisory_source": "AI_PROVIDER",
            "risk_level": risk,
            "recommendations": cleaned_recs,
            "fallback_reason": None,
        }
    except Exception as exc:
        logger.warning("AI Provider call failed (%s); using Rule-Based Fallback Engine.", exc)
        result = generate_rule_based_recommendations(plan_data)
        result["fallback_reason"] = "AI provider unavailable or timed out; safely served via Rule-Based Fallback Engine."
        return result
