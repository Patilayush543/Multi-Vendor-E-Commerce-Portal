from django.contrib.auth.models import User
from myapp.models import Invoice
from django.test import RequestFactory
from myapp import views

user = User.objects.filter(username='testbuyer').first()
if not user:
    print('No test user found')
else:
    inv = Invoice.objects.filter(orders__user=user).order_by('-issued_at').first()
    if not inv:
        print('No invoice found for test user')
    else:
        rf = RequestFactory()
        req = rf.get(f'/download-invoice/invoice/{inv.id}/')
        req.user = user
        resp = views.download_consolidated_invoice(req, inv.id)
        print('Response type:', type(resp), 'status:', getattr(resp, 'status_code', None))
        try:
            data = resp.content
            print('PDF bytes length:', len(data))
        except Exception as e:
            print('Could not read response content:', e)
