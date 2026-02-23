from django.contrib.auth.models import User
from myapp.models import Product, Cart, CartItem, CartOrder, Invoice
from django.test import Client
from django.conf import settings

# Create test user
username = 'testbuyer'
email = 'testbuyer@example.com'
password = 'password123'
user, created = User.objects.get_or_create(username=username, defaults={'email': email})
if created:
    user.set_password(password)
    user.save()

# Create product if none exists
product, pcreated = Product.objects.get_or_create(title='Test Product', defaults={
    'brand': 'TestBrand',
    'price': 199.99,
    'description': 'A product for automated test',
    'category': 'tech',
    'image_url': 'https://example.com/image.jpg',
    'stock_count': 10,
})

# Ensure cart and cartitem
cart, _ = Cart.objects.get_or_create(user=user)
CartItem.objects.filter(cart=cart).delete()
ci = CartItem.objects.create(cart=cart, product=product, quantity=2)

# Use Django test client to login and post to confirm-order
client = Client()
logged_in = client.login(username=username, password=password)
print('logged_in=', logged_in)
resp = client.post('/confirm-order/', {'address': '123 Test St', 'mobile': '9998887777'})
print('POST /confirm-order/ status_code=', resp.status_code)

# Check created invoices
invoices = Invoice.objects.filter(orders__user=user).distinct()
print('Invoices count=', invoices.count())
for inv in invoices:
    print('Invoice', inv.invoice_number, 'total=', inv.total, 'orders=', list(inv.orders.values_list('id', flat=True)))

# Print response snippet
print('Response length:', len(resp.content))
print('Response contains invoice list?', b'invoice' in resp.content.lower())
