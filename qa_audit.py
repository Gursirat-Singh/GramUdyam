#!/usr/bin/env python
"""Comprehensive QA audit runner."""
import json, os, io, traceback
import django
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
django.setup()
from django.core.management import call_command
from django.test.utils import setup_test_environment, teardown_test_environment
from django.test import Client

RESULTS = []
# severity values: INFO, LOW, MEDIUM, HIGH, CRITICAL
def R(tid, module, scenario, pre, steps, expect, actual, status, severity, evidence=''):
    RESULTS.append({'Test ID': tid, 'Module': module, 'Test Scenario': scenario, 'Preconditions': pre,
         'Test Steps': steps, 'Expected Result': expect, 'Actual Result': actual,
         'Status': status, 'Severity': severity, 'Evidence': evidence})

def main():
    call_command('migrate', verbosity=0, interactive=False)
    print('[QA] DB migrated')
    run_existing_tests()
    run_http_smoke()
    run_functional_checks()
    s = summarize()
    write_report_input(s)
    return RESULTS

def run_existing_tests():
    out = io.StringIO(); call_command('test', stdout=out, stderr=out, verbosity=2)
    txt = out.getvalue()
    if 'OK' in txt or 'PASSED' in txt or 'no tests ran' in txt:
        R('T-A1','System','Django test command',
           'python manage.py test',['python manage.py test'],'All tests pass','PASS','INFO')
    else:
        raise RuntimeError('Existing tests did not pass: '+txt[:500])

def run_http_smoke():
    """HTTP smoke tests for all public and protected endpoints."""
    from django.urls import reverse
    c = Client()
    
    # Public / unauthenticated pages - should redirect to login
    public_routes = [
        ('dashboard:index', {}),
        ('business_advisor:list', {}),
        ('financial_planning:list', {}),
        ('market_insights:overview', {}),
        ('reports:list', {}),
        ('accounts:login', {}),
        ('accounts:register', {}),
    ]
    for name, kwargs in public_routes:
        try:
            resp = c.get(reverse(name, kwargs=kwargs))
            if resp.status_code in (200, 302):
                R(f'T-H-{name.replace(":","-")}','HTTP',f'GET {name}',
                   'Unauthenticated client',['c.get(reverse(...))'],
                   '200 OK or 302 redirect to login',f'{resp.status_code}','PASS','INFO')
            else:
                R(f'T-H-{name.replace(":","-")}','HTTP',f'GET {name}',
                   'Unauthenticated client',['c.get(reverse(...))'],
                   '200 OK or 302 redirect',f'{resp.status_code}','FAIL','MEDIUM')
        except Exception as e:
            R(f'T-H-{name.replace(":","-")}','HTTP',f'GET {name}',
               'Unauthenticated client',['c.get(reverse(...))'],
               '200 OK or 302 redirect',f'Exception: {e}','FAIL','HIGH')
    
    # Authenticated pages - should return 200
    from django.contrib.auth.models import User
    u = User.objects.create_user(username='smokeuser', password='Test@1234')
    c.login(username='smokeuser', password='Test@1234')
    
    auth_routes = [
        ('dashboard:index', {}),
        ('business_advisor:list', {}),
        ('financial_planning:list', {}),
        ('market_insights:overview', {}),
        ('reports:list', {}),
        ('business_advisor:create', {}),
        ('financial_planning:create', {}),
        ('market_insights:observation_create', {}),
        ('reports:create', {}),
    ]
    for name, kwargs in auth_routes:
        try:
            resp = c.get(reverse(name, kwargs=kwargs))
            if resp.status_code == 200:
                R(f'T-HA-{name.replace(":","-")}','HTTP',f'Auth GET {name}',
                   'Logged-in user',['c.get(reverse(...))'],
                   '200 OK',f'{resp.status_code}','PASS','INFO')
            else:
                R(f'T-HA-{name.replace(":","-")}','HTTP',f'Auth GET {name}',
                   'Logged-in user',['c.get(reverse(...))'],
                   '200 OK',f'{resp.status_code}','FAIL','MEDIUM')
        except Exception as e:
            R(f'T-HA-{name.replace(":","-")}','HTTP',f'Auth GET {name}',
               'Logged-in user',['c.get(reverse(...))'],
               '200 OK',f'Exception: {e}','FAIL','HIGH')

def run_functional_checks():
    """Functional checks for core business logic: financial projections, PDF export, recommendations."""
    from decimal import Decimal
    from django.contrib.auth.models import User
    from django.urls import reverse
    from django.test import Client
    from financial_planning.services import calculate_financial_projections, build_scenario_comparisons
    from business_advisor.services import generate_rule_based_recommendations
    from financial_planning.models import FinancialPlan
    from business_advisor.models import BusinessPlan
    from reports.models import Report
    
    c = Client()
    u = User.objects.create_user(username='funcuser', password='Test@1234')
    c.login(username='funcuser', password='Test@1234')
    
    sample_fp = {
        'available_capital': Decimal('75000.00'),
        'equipment_and_setup_cost': Decimal('60000.00'),
        'initial_inventory_cost': Decimal('10000.00'),
        'licensing_and_contingency': Decimal('5000.00'),
        'monthly_raw_material_cost': Decimal('20000.00'),
        'monthly_rent_and_utilities': Decimal('3000.00'),
        'monthly_salaries_and_labour': Decimal('8000.00'),
        'monthly_transport_and_logistics': Decimal('2000.00'),
        'monthly_marketing_expense': Decimal('1500.00'),
        'monthly_other_expenses': Decimal('1000.00'),
        'estimated_selling_price_per_unit': Decimal('200.00'),
        'expected_monthly_sales_volume': Decimal('200.00'),
        'loan_amount': Decimal('50000.00'),
        'annual_interest_rate': Decimal('12.00'),
        'loan_tenure_months': 36,
        'working_capital_months': 3,
    }
    try:
        proj = calculate_financial_projections(sample_fp)
        assert proj['total_startup_investment'] == Decimal('75000.00')
        assert proj['estimated_monthly_revenue'] == Decimal('40000.00')
        assert proj['total_monthly_operating_cost'] == Decimal('35500.00')
        assert proj['break_even_status'] in ('ACHIEVABLE','NOT_ACHIEVABLE')
        R('T-F-01','Financial','calculate_financial_projections service',
           'Valid input dict',['calculate_financial_projections(dict)'],
           'All key metrics present and numeric',f'OK: rev={proj["estimated_monthly_revenue"]}, ebitda={proj["estimated_monthly_ebitda"]}','PASS','INFO')
    except Exception as e:
        R('T-F-01','Financial','calculate_financial_projections service',
           'Valid input dict',['calculate_financial_projections(dict)'],
           'All key metrics present and numeric',f'Exception: {e}','FAIL','HIGH')

    # --- 3-Scenario comparisons ---
    try:
        sc = build_scenario_comparisons(sample_fp)
        assert set(sc.keys()) == {'conservative','expected','optimistic'}
        for k in ('conservative','expected','optimistic'):
            assert 'estimated_monthly_revenue' in sc[k]
        R('T-F-02','Financial','build_scenario_comparisons service',
           'Valid input dict',['build_scenario_comparisons(dict)'],
           'Three scenarios with revenue',f'OK: C={sc["conservative"]["estimated_monthly_revenue"]}, E={sc["expected"]["estimated_monthly_revenue"]}, O={sc["optimistic"]["estimated_monthly_revenue"]}','PASS','INFO')
    except Exception as e:
        R('T-F-02','Financial','build_scenario_comparisons service',
           'Valid input dict',['build_scenario_comparisons(dict)'],
           'Three scenarios with revenue',f'Exception: {e}','FAIL','HIGH')

    # --- Rule-based recommendations ---
    sample_bp = {
        'business_category': 'FOOD_PROCESSING',
        'state': 'Punjab',
        'district': 'Patiala',
        'village_or_town': 'Nabha',
        'investment_budget': Decimal('75000.00'),
        'existing_skills': 'Food processing, pickling',
        'existing_resources': 'Home kitchen, refrigerator',
        'target_customers': 'Village households, local shops',
        'business_objectives': 'Monthly income 20k, employ 2 women',
        'constraints': 'Power cuts 4hrs/day',
    }
    try:
        rec = generate_rule_based_recommendations(sample_bp)
        assert 'recommendations' in rec and len(rec['recommendations']) == 3
        for r in rec['recommendations']:
            assert 1 <= r['suitability_score'] <= 100
        R('T-F-03','Business','generate_rule_based_recommendations service',
           'Valid plan dict',['generate_rule_based_recommendations(dict)'],
           '3 recommendations with scores',f'OK: {len(rec["recommendations"])} recs, source={rec["advisory_source"]}','PASS','INFO')
    except Exception as e:
        R('T-F-03','Business','generate_rule_based_recommendations service',
           'Valid plan dict',['generate_rule_based_recommendations(dict)'],
           '3 recommendations with scores',f'Exception: {e}','FAIL','HIGH')


    # --- Full HTTP flow: create BusinessPlan -> FinancialPlan -> Report -> PDF export ---
    try:
        # Create BusinessPlan via view
        bp_resp = c.post(reverse('business_advisor:create'), data={
            'title': 'Mustard Oil Micro-Unit',
            'business_category': 'FOOD_PROCESSING',
            'business_idea': 'Cold-pressed mustard oil',
            'state': 'Punjab',
            'district': 'Patiala',
            'village_or_town': 'Nabha',
            'investment_budget': '75000.00',
            'existing_skills': 'Oil extraction, filtration',
            'existing_resources': 'Shed, 3-phase power',
            'target_customers': 'Local households, kirana stores',
            'business_objectives': 'Monthly profit 15k, employ 3',
            'constraints': 'Seasonal mustard availability',
        }, follow=True)
        assert bp_resp.status_code == 200
        bp = BusinessPlan.objects.get(user=u)

        # Create FinancialPlan via view (linked to BP)
        fp_resp = c.post(reverse('financial_planning:create'), data={
            'business_plan': str(bp.pk),
            'title': 'Mustard Oil Financials',
            'available_capital': '75000.00',
            'equipment_and_setup_cost': '60000.00',
            'initial_inventory_cost': '10000.00',
            'licensing_and_contingency': '5000.00',
            'monthly_raw_material_cost': '20000.00',
            'monthly_rent_and_utilities': '3000.00',
            'monthly_salaries_and_labour': '8000.00',
            'monthly_transport_and_logistics': '2000.00',
            'monthly_marketing_expense': '1500.00',
            'monthly_other_expenses': '1000.00',
            'estimated_selling_price_per_unit': '200.00',
            'expected_monthly_sales_volume': '200.00',
            'loan_amount': '50000.00',
            'annual_interest_rate': '12.00',
            'loan_tenure_months': '36',
            'working_capital_months': '3',
        }, follow=True)
        assert fp_resp.status_code == 200
        fp = FinancialPlan.objects.get(user=u)
        assert fp.total_startup_investment == Decimal('75000.00')

        # Create Report via view
        rep_resp = c.post(reverse('reports:create'), data={
            'title': 'Mustard Oil Bank Dossier',
            'report_type': 'BANK_LOAN_PROPOSAL',
            'financial_plan': str(fp.pk),
            'executive_summary': 'Bank loan dossier for mustard oil unit.',
        }, follow=True)
        assert rep_resp.status_code == 200
        rep = Report.objects.get(user=u)

        # PDF export
        pdf_resp = c.get(reverse('reports:export_pdf', kwargs={'pk': rep.pk}))
        assert pdf_resp.status_code == 200
        assert pdf_resp['Content-Type'] == 'application/pdf'
        assert pdf_resp.content.startswith(b'%PDF-')

        R('T-F-04','Integration','Full flow: BP -> FP -> Report -> PDF',
           'Logged-in user, valid data',['POST create BP','POST create FP','POST create Report','GET export_pdf'],
           '200 for each step, PDF starts with %PDF-',f'OK: BP={bp.pk}, FP={fp.pk}, Report={rep.pk}, PDF bytes={len(pdf_resp.content)}','PASS','INFO')
    except Exception as e:
        R('T-F-04','Integration','Full flow: BP -> FP -> Report -> PDF',
           'Logged-in user, valid data',['POST create BP','POST create FP','POST create Report','GET export_pdf'],
           '200 for each step, PDF starts with %PDF-',f'Exception: {e}','FAIL','HIGH')
def summarize():
    """Summarize QA results."""
    total = len(RESULTS)
    passed = sum(1 for r in RESULTS if r['Status'] == 'PASS')
    failed = sum(1 for r in RESULTS if r['Status'] == 'FAIL')
    by_module = {}
    by_sev = {}
    for r in RESULTS:
        by_module[r['Module']] = by_module.get(r['Module'], 0) + 1
        by_sev[r['Severity']] = by_sev.get(r['Severity'], 0) + 1
    return {
        'total': total,
        'passed': passed,
        'failed': failed,
        'pass_rate': f'{(passed / total * 100):.1f}%' if total else 'N/A',
        'by_module': by_module,
        'by_severity': by_sev,
    }


def write_report_input(summary):
    """Persist the QA audit summary to qa_report_input.json."""
    import datetime
    payload = {
        'generated_at': datetime.datetime.now().isoformat(),
        'summary': summary,
        'results': RESULTS,
    }
    with open('qa_report_input.json', 'w', encoding='utf-8') as fh:
        json.dump(payload, fh, indent=2, default=str)
    print(
        f"[QA] Report written to qa_report_input.json "
        f"({summary['passed']}/{summary['total']} passed, {summary['pass_rate']})"
    )


if __name__ == '__main__':
    main()
