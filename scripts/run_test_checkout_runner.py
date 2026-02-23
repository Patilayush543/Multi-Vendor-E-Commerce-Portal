import os
import django
from pathlib import Path
import sys

d = Path(__file__).resolve().parent
os.chdir(d.parent)
sys.path.insert(0, str(d.parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ECommerce.settings')
django.setup()

# Execute the test script
with open(d / 'test_checkout.py', 'r', encoding='utf-8') as f:
    code = f.read()
exec(compile(code, str(d / 'test_checkout.py'), 'exec'))
print('Runner finished')
