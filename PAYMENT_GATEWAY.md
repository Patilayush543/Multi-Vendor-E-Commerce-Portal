# Razorpay Payment Gateway Implementation

## Overview

This Django e-commerce application now supports a comprehensive payment gateway system with three payment methods:

1. **Cash on Delivery (COD)** - Default payment method, no online processing
2. **Razorpay Gateway** - Secure online payment via Razorpay (Card, UPI, NetBanking, Wallets)
3. **UPI QR / Manual Transfer** - Manual UPI payment with transaction ID tracking

## Database Schema

### CartOrder Model Updates

```python
class CartOrder(models.Model):
    # ... existing fields ...
    
    # New payment-related fields
    PAYMENT_METHOD_CHOICES = [
        ('cod', 'Cash on Delivery'),
        ('razorpay', 'Razorpay'),
        ('upi_qr', 'UPI QR / Manual Transfer'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
    ]
    
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default='cod'
    )
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='pending'
    )
    transaction_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Razorpay Order ID or UPI Transaction ID"
    )
```

## Configuration

### Environment Variables (.env file)

```env
# Razorpay API Keys - Get from https://razorpay.com/dashboard/settings/api-keys
RAZORPAY_KEY_ID=rzp_test_xxxxx        # Test or Live Key ID
RAZORPAY_KEY_SECRET=xxxxxxxxxxxxx     # Test or Live Key Secret
RAZORPAY_WEBHOOK_ID=wh_xxxxxxxxxxxxx  # Optional: Webhook ID
```

### Settings Configuration (ECommerce/settings.py)

```python
# Payment Gateway Configuration
RAZORPAY_KEY_ID = os.getenv('RAZORPAY_KEY_ID', '')
RAZORPAY_KEY_SECRET = os.getenv('RAZORPAY_KEY_SECRET', '')
RAZORPAY_WEBHOOK_ID = os.getenv('RAZORPAY_WEBHOOK_ID', '')
```

## URL Routes

Add these routes to `myapp/urls.py`:

```python
# Payment Gateway
path('verify-razorpay/', views.verify_razorpay, name='verify_razorpay'),
path('order-success/', views.order_success, name='order_success'),
```

## API Endpoints

### 1. Checkout Endpoint (POST /checkout/)
**Purpose**: Initiate payment process
**Request Data**:
```json
{
    "address": "123 Main St, City, State",
    "mobile": "9876543210",
    "payment_method": "razorpay",  // 'cod' | 'razorpay' | 'upi_qr'
    "transaction_id": ""  // Required only for UPI QR
}
```

**Response**:
- **COD/UPI QR**: Redirects to order success page
- **Razorpay**: Redirects to razorpay_payment.html with order details

### 2. Razorpay Verification Endpoint (POST /verify-razorpay/)
**Purpose**: Verify payment signature and update order status
**Request**:
```json
{
    "razorpay_order_id": "order_xxxxx",
    "razorpay_payment_id": "pay_xxxxx",
    "razorpay_signature": "signature_xxxxx"
}
```

**Response**:
```json
{
    "status": "success",
    "message": "Payment verified successfully"
}
```

### 3. Order Success Endpoint (GET /order-success/)
**Purpose**: Display order confirmation
**Shows**: Payment method, status, invoices, download links

## Payment Flows

### Flow 1: Cash on Delivery

```
User selects COD
    ↓
Order created with payment_status='pending'
    ↓
Invoices generated
    ↓
Order Success Page (shows "Pay at Delivery")
    ↓
Admin confirms delivery & payment
    ↓
Payment status updated to 'paid'
```

### Flow 2: Razorpay Payment

```
User selects Razorpay at checkout
    ↓
Backend creates Razorpay order (₹ amount in paise)
    ↓
Redirect to razorpay_payment.html
    ↓
Razorpay Checkout modal opens
    ↓
User pays (Card/UPI/NetBanking/Wallet)
    ↓
Frontend sends payment details to /verify-razorpay/
    ↓
Backend verifies HMAC SHA256 signature
    ↓
If valid: Update order payment_status='paid'
    ↓
Redirect to Order Success Page (shows "✓ Payment Confirmed")
```

### Flow 3: UPI QR / Manual Transfer

```
User selects UPI QR at checkout
    ↓
Optional: Display UPI QR code for amount
    ↓
Order created with payment_status='pending'
    ↓
User provides transaction ID
    ↓
Order Success Page (shows "⏳ Awaiting Payment Confirmation")
    ↓
Admin verifies transaction
    ↓
Admin marks order as paid in Django admin
```

## Frontend Implementation

### Templates

1. **checkout.html**
   - Radio buttons for payment method selection
   - JavaScript to toggle transaction ID field for UPI QR
   - Form submission to confirm_order view

2. **razorpay_payment.html**
   - Order summary with amount in ₹
   - Razorpay Checkout widget integration
   - Payment success/error handling
   - Auto-redirect to order success on verification

3. **order_success.html**
   - Payment method display
   - Status badge (✓ Paid / ⏳ Pending / 🚚 COD)
   - Contextual messages
   - Invoice download links
   - Navigation buttons

## Security Implementation

### Signature Verification

Razorpay payments are verified using HMAC SHA256:

```python
import hmac
import hashlib

verify_string = f"{razorpay_order_id}|{razorpay_payment_id}"
computed_signature = hmac.new(
    razorpay_key_secret.encode(),
    verify_string.encode(),
    hashlib.sha256
).hexdigest()

if computed_signature == razorpay_signature:
    # Payment is valid
```

### Security Measures
- CSRF protection on all forms
- Login required for payment operations
- HTTPS recommended for production
- Keys stored in environment variables (not hardcoded)
- Transaction audit trail (stored transaction_id)
- Signature verification for all payments

## Testing

### Test Mode (Sandbox)

Use Razorpay test credentials:
- Key ID: `rzp_test_xxxxx`
- Key Secret: `xxxxxxxxxxxxx`

Test cards available on Razorpay dashboard

### Production Mode

1. Get live credentials from Razorpay dashboard
2. Update RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET in .env
3. Set DJANGO_DEBUG=False in production
4. Enable HTTPS

## Dashboard Integration

### For Customers
- View payment method and status in dashboard
- Download invoices
- Track payment status

### For Admin
- Manage payment method in admin panel
- Mark UPI payments as verified
- Process refunds
- View payment reports

## Future Enhancements

1. **Webhook Handler** - Real-time payment updates from Razorpay
2. **Partial Refunds** - Support for partial and full refunds
3. **Recurring Payments** - Subscription and recurring payment support
4. **Multiple Currencies** - Support for other currencies
5. **Payment Analytics** - Dashboard with payment statistics
6. **QR Code Generation** - Auto-generate UPI QR codes
7. **Payment Scheduling** - Schedule payments and reminders
8. **Multiple Gateways** - Add PayPal, Stripe, Google Pay, Apple Pay

## Troubleshooting

### "Razorpay keys not configured"
- Check .env file has RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET
- Ensure environment variables are loaded

### "Payment signature verification failed"
- Verify Razorpay keys are correct
- Check signature calculation logic
- Ensure order ID matches

### "Order not found"
- Verify order was created before payment
- Check user authentication
- Ensure correct user is making request

## Support & Documentation

- [Razorpay API Documentation](https://razorpay.com/docs/api/payments/create-standard-payment/)
- [Razorpay Python SDK](https://github.com/razorpay/razorpay-python)
- [Razorpay Dashboard](https://razorpay.com/dashboard)

---

**Implementation Date:** February 23, 2026
**Status:** ✅ Production Ready
**Version:** 1.0
