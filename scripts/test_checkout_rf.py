from django.contrib.auth.models import User
from myapp.models import Product, Cart, CartItem, CartOrder, Invoice
from django.test import RequestFactory
from myapp import views
from django.conf import settings

# Prepare user & product (assumes previous script ran or create if missing)
username = 'testbuyer'
email = 'testbuyer@example.com'
password = 'password123'
user, _ = User.objects.get_or_create(username=username, defaults={'email': email})
# Ensure password is set for completeness (not needed for RequestFactory)
user.set_password(password)
user.save()

product, _ = Product.objects.get_or_create(title='Test Product', defaults={
    'brand': 'TestBrand',
    'price': 199.99,
    'description': 'A product for automated test',
    'category': 'tech',
    'image_url': 'https://example.com/image.jpg',
    'stock_count': 10,
})

# Cart setup
cart, _ = Cart.objects.get_or_create(user=user)
CartItem.objects.filter(cart=cart).delete()
ci = CartItem.objects.create(cart=cart, product=product, quantity=2)

# Build request via RequestFactory to avoid ALLOWED_HOSTS issues
rf = RequestFactory()
req = rf.post('/confirm-order/', {'address': '123 Test St', 'mobile': '9998887777'})
req.user = user

# Call view directly
resp = views.confirm_order(req)
print('View returned:', type(resp), getattr(resp, 'status_code', 'no status_code'))

# Check created invoices
invoices = Invoice.objects.filter(orders__user=user).distinct()
print('Invoices count=', invoices.count())
for inv in invoices:
    print('Invoice', inv.invoice_number, 'total=', inv.total, 'orders=', list(inv.orders.values_list('id', flat=True)))

# If view returned a TemplateResponse, render content length
try:
    content = resp.content
    print('Response length:', len(content))
    print('Response contains invoice?', b'invoice' in content.lower())
except Exception as e:
    print('Could not read response content:', e)
