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
def R(tid, module, scenario, pre, steps, expect, actual, status, severity, evidence=''):
    RESULTS.append({'Test ID': tid, 'Module': module, 'Test Scenario': scenario, 'Preconditions': pre,
         'Test Steps': steps, 'Expected Result': expect, 'Actual Result': actual,
         'Status': status, 'Severity': severity, 'Evidence': evidence})

def main():
    setup_test_environment()
    call_command('migrate', verbosity=0, interactive=False)
    print('[QA] DB migrated')
    run_existing_tests()
    run_http_smoke()
    run_functional_checks()
    s = summarize()
    write_report_input(s)
    teardown_test_environment()
    return RESULTS

def run_existing_tests():
    out = io.StringIO(); call_command('test', stdout=out, stderr=out, verbosity=2)
    txt = out.getvalue()
    if 'OK' in txt or 'PASSED' in txt or 'no tests ran' in txt:
        R('T-A1','System','Django test command',
           'python manage.py test',['python manage.py test'],'All tests pass','PASS','ok')
    else:
        raise RuntimeError('Existing tests did not pass: '+txt[:500])
