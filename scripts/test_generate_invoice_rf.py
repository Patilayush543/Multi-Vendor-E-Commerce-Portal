from django.contrib.auth.models import User
from myapp.models import CartOrder
from django.test import RequestFactory
from myapp import views

# Prepare
user = User.objects.filter(username='testbuyer').first()
if not user:
    print('No test user found')
else:
    order = CartOrder.objects.filter(user=user).first()
    if not order:
        print('No CartOrder found for test user')
    else:
        rf = RequestFactory()
        req = rf.get(f'/download-invoice/{order.id}/')
        req.user = user
        resp = views.generate_invoice(req, order.id)
        print('Response type:', type(resp), 'status:', getattr(resp, 'status_code', None))
        try:
            data = resp.content
            print('PDF bytes length:', len(data))
        except Exception as e:
            print('Could not read response content:', e)
