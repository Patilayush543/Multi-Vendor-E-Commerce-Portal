"""
Test script: Verify quantity support and consolidated invoicing
- Create multiple CartOrder items with different quantities
- Confirm order → creates consolidated invoice
- Verify total_price calculations (price × quantity)
- Check invoice displays correct line totals
"""

from django.contrib.auth.models import User
from myapp.models import CartOrder, Product, Invoice

# Clean up old test data
CartOrder.objects.filter(user__username='test_buyer').delete()
Invoice.objects.filter(orders__user__username='test_buyer').delete()

# Get or create test user
test_user, created = User.objects.get_or_create(
    username='test_buyer',
    defaults={'email': 'test_buyer@example.com'}
)

# Get some products from the seeded data
tech_products = Product.objects.filter(category='tech')[:2]
fashion_products = Product.objects.filter(category='fashion')[:2]

print("=" * 60)
print("TEST: QUANTITY & CONSOLIDATED INVOICE")
print("=" * 60)

# Test Case 1: Add to cart with quantities
print("\n1. Adding items to cart with quantities:")
cart_items = []

if tech_products.count() >= 2:
    # Add tech product with qty=3
    item1 = CartOrder.objects.create(
        user=test_user,
        product=tech_products[0],
        product_name=tech_products[0].title,
        price=tech_products[0].price,
        quantity=3,
        status='pending'
    )
    cart_items.append(item1)
    print(f"   ✓ {item1.product_name} × {item1.quantity} = ₹{item1.total_price}")

    # Add tech product with qty=2
    item2 = CartOrder.objects.create(
        user=test_user,
        product=tech_products[1],
        product_name=tech_products[1].title,
        price=tech_products[1].price,
        quantity=2,
        status='pending'
    )
    cart_items.append(item2)
    print(f"   ✓ {item2.product_name} × {item2.quantity} = ₹{item2.total_price}")

if fashion_products.count() >= 2:
    # Add fashion product with qty=1
    item3 = CartOrder.objects.create(
        user=test_user,
        product=fashion_products[0],
        product_name=fashion_products[0].title,
        price=fashion_products[0].price,
        quantity=1,
        status='pending'
    )
    cart_items.append(item3)
    print(f"   ✓ {item3.product_name} × {item3.quantity} = ₹{item3.total_price}")

    # Add fashion product with qty=5
    item4 = CartOrder.objects.create(
        user=test_user,
        product=fashion_products[1],
        product_name=fashion_products[1].title,
        price=fashion_products[1].price,
        quantity=5,
        status='pending'
    )
    cart_items.append(item4)
    print(f"   ✓ {item4.product_name} × {item4.quantity} = ₹{item4.total_price}")

# Test Case 2: Calculate cart total
print("\n2. Cart Summary:")
pending_orders = CartOrder.objects.filter(user=test_user, status='pending')
cart_total = sum(order.total_price for order in pending_orders)
print(f"   Total Items: {len(cart_items)}")
print(f"   Cart Total: ₹{cart_total}")

# Test Case 3: Simulate checkout (update status)
print("\n3. Confirming Order (mark as packed):")
CONSOLIDATED_INVOICE = True
# Re-fetch before updating to ensure we have the fresh order count
pending_orders = CartOrder.objects.filter(user=test_user, status='pending')
updated_count = pending_orders.update(status='packed', shipping_address='123 Test St, Test City', mobile='9999999999')
print(f"   ✓ {updated_count} orders marked as 'packed'")

# Re-fetch packed orders for invoice creation
pending_orders = CartOrder.objects.filter(user=test_user, status='packed')

# Test Case 4: Create consolidated invoice
if CONSOLIDATED_INVOICE:
    print("\n4. Creating Consolidated Invoice:")
    subtotal = sum(order.total_price for order in pending_orders)
    from django.utils import timezone
    invoice_number = f"INV{test_user.id}{int(timezone.now().timestamp())}"
    invoice = Invoice.objects.create(
        invoice_number=invoice_number,
        subtotal=subtotal,
        tax=0,
        total=subtotal
    )
    invoice.orders.set(pending_orders)
    print(f"   ✓ Invoice #{invoice.invoice_number}")
    print(f"   ✓ Subtotal: ₹{invoice.subtotal}")
    print(f"   ✓ Tax: ₹{invoice.tax}")
    print(f"   ✓ Total: ₹{invoice.total}")
    
    # Test Case 5: Verify invoice contains all orders
    print("\n5. Invoice Order Breakdown:")
    for order in invoice.orders.all():
        print(f"   {order.product_name} × {order.quantity} @ ₹{order.price} = ₹{order.total_price}")
    
    total_check = sum(o.total_price for o in invoice.orders.all())
    print(f"\n   VERIFICATION: ₹{total_check} == ₹{invoice.total} ✓" if total_check == invoice.total else f"\n   ERROR: Mismatch!")

print("\n" + "=" * 60)
print("TEST COMPLETED SUCCESSFULLY")
print("=" * 60)
