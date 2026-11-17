import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()
from django.test.utils import get_runner
from django.conf import settings
runner = get_runner(settings)(verbosity=2)
failures = runner.run_tests(['accounts', 'dashboard', 'business_advisor', 'financial_planning', 'market_insights', 'reports'])
print('FAILURES:', failures)