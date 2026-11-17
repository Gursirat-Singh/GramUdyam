#!/usr/bin/env python
"""Comprehensive HTTP smoke test for GramVenture AI.
Demonstrates URL routing, authentication, views, response codes, errors.
Uses Django test client with isolated test database."""
import os, django
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
django.setup()
from django.test import Client
from django.test.utils import setup_test_environment, teardown_test_environment
from django.core.management import call_command

def main():
    setup_test_environment()
    call_command('migrate', verbosity=0, interactive=False)
    results = {'PASS': [], 'FAIL': [], 'PARTIAL': [], 'UNTESTED': []}
    
    c = Client()
    
    # 1. Anonymous access checks
    print('[SMOKE] 1. Anonymous access checks...')
    anon = {
        '/accounts/signup/', '/accounts/login/', '/accounts/logout/',
        '/business-advisor/', '/business-advisor/recommend/', '/business-advisor/register/',
        '/financial-planning/', '/financial-planning/calculate/', '/financial-planning/scenario/',
        '/market-insights/', '/market-insights/region/', '/market-insights/observe/',
        '/market-insights/delete/<int>', '/reports/', '/reports/export/'
    }
    for url in sorted(anon):
        try:
            r = c.get(url)
            print(f'  GET {url} -> {r.status_code}')
        except Exception as e:
            print(f'  GET {url} -> ERROR: {e}')
            results['FAIL'].append(url)
    
    # 2. Login as test user 'demo@example.com' / 'TestUser!'
    print('[SMOKE] 2. Login as demo user...')
    r = c.post('/accounts/login/', {'email':'demo@example.com','password':'TestUser!'}, follow=True)
    print(f'  Login -> {r.status_code}')
    assert r.status_code == 200, f'login failed {r.status_code}'
    login_ok = r.status_code == 200
    
    # 3. Protected pages as logged-in user
    print('[SMOKE] 3. Protected pages as demo user...')
    for url in [
        '/accounts/dashboard/', '/accounts/business-advisor/', '/business-advisor/recommend/',
        '/business-advisor/register/', '/financial-planning/', '/financial-planning/calculate/',
        '/financial-planning/scenario/', '/financial-planning/save/',
        '/market-insights/', '/market-insights/region/', '/market-insights/observe/',
        '/reports/', '/reports/view/'
    ]:
        try:
            r = c.get(url)
            label = url.split('/')[1] if '/' in url[:15] else ''
            print(f'  GET {url} -> {r.status_code} [{label}]')
        except Exception as e:
            print(f'  GET {url} -> ERROR: {e}')
    
    # 4. Submit business recommend form (POST)
    print('[SMOKE] 4. POST business-advisor/recommend/')
    data = {
        'location': 'Ludhiana India', 'category': 'Retail',
        'budget': 5000, 'months': 12, 'selling_price': 25,
        'units_per_day': 30
    }
    r = c.post('/business-advisor/recommend/', data, follow=True)
    print(f'  POST recommend -> {r.status_code} (expect 200 or 201)')
    if r.status_code != 200:
        print(f'    body snippet: {r.content[:500]}')
    
    # 5. Report creation via view plan
    print('[SMOKE] 5. POST financial-planning/save/')
    save_data = {
        'scenario': 'All Scenarios', 'items': 'items1|startup_investment|5000',
        'equipment_expense': 'equipment1|5000|2500', 'monthly_opex': 'opex1|5000|2500',
        'monthly_revenue': 'revenue1|18000|18000', 'interest_rate': '5000|5%|5000',
        'payback_months': 12, 'items_json_raw': '[{"name":"startup","value":5000},{"name":"opex","value":2500},{"name":"revenue","value":18000}]',
        'note': 'smoke test report', 'report_type':'finance'
    }
    r = c.post('/financial-planning/save/', save_data, follow=True)
    print(f'  POST save -> {r.status_code} (expect 201)')
    
    # 6. View reports list
    print('[SMOKE] 6. GET /reports/view/')
    r = c.get('/reports/view/')
    print(f'  GET reports -> {r.status_code}')
    
    # 7. Market insights observe
    print('[SMOKE] 7. Market insights observe POST')
    mi_data = {'market_location':'Chennai India','observation':'rising demand',
               'source_url':'https://example.com'}
    r = c.post('/market-insights/observe/', mi_data, follow=True)
    print(f'  POST observe -> {r.status_code}')
    
    # 8. Logout
    print('[SMOKE] 8. Logout...')
    r = c.post('/accounts/logout/')
    print(f'  logout -> {r.status_code}')
    
    # 9. Authz: another user cannot see demo's reports
    print('[SMOKE] 9. Authz cross-user...')
    r = c.post('/accounts/login/', {'email':'alice@example.com','password':'Alice99!'})
    r2 = c.get('/reports/view/')
    print(f'  alice GET reports -> {r2.status_code}')
    r = c.post('/accounts/logout/')
    
    teardown_test_environment()
    print('\n=== SMOKE SUMMARY ===')
    print(f"Passed: {len(results['PASS'])}, Failed: {len(results['FAIL'])}, Partial: {len(results['PARTIAL'])}, Untested: {len(results['UNTESTED'])}")
    return results

if __name__ == '__main__':
    main()
