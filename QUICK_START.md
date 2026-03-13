# Razorpay Payment Gateway - Quick Start Guide

## 🚀 Getting Started in 5 Minutes

### Step 1: Verify Installation
```bash
cd "d:\trying to open\Django-ECommerce-Web-main"
.\.venv\Scripts\python.exe manage.py check
```
✅ Should say: "System check identified no issues (0 silenced)"

### Step 2: Get Razorpay Test Keys
1. Visit https://razorpay.com/dashboard
2. Go to Settings → API Keys
3. Stay in **Test Mode** for testing
4. Copy your **Key ID** (starts with `rzp_test_`)
5. Copy your **Key Secret** (hidden by default, click to reveal)

### Step 3: Update .env File
Edit `.env` file in the project root:
```env
RAZORPAY_KEY_ID=rzp_test_xxxxxxxxxxxxx
RAZORPAY_KEY_SECRET=xxxxxxxxxxxxxxxxxxxxx
```

### Step 4: Start Django Server
```bash
.\.venv\Scripts\python.exe manage.py runserver
```
✅ Server running at: http://127.0.0.1:8000

### Step 5: Test Payment Gateway
1. Open http://127.0.0.1:8000
2. Add products to cart
3. Click "Checkout"
4. Choose payment method:
   - **Cash on Delivery**: Select and confirm
   - **Razorpay**: Click "Pay Now" → Use test card
   - **UPI QR**: Enter transaction ID

---

## 💳 Test Razorpay Cards

Use these test card numbers for different scenarios:

**Successful Payment:**
- Card: `4111 1111 1111 1111`
- Expiry: Any future date (e.g., `12/25`)
- CVV: Any 3 digits (e.g., `123`)

**Failed Payment:**
- Card: `4000 0000 0000 0002`

**3D Secure Verification:**
- Card: `4000 0200 0000 0000`

---

## 📋 Payment Method Selection

### Cash on Delivery (COD)
- ✅ Default option
- ✅ No payment processing
- ✅ User pays when order is delivered
- 📦 Status: "🚚 Pay at Delivery"

### Razorpay
- ✅ Secure online payment
- ✅ Supports Card, UPI, NetBanking, Wallet
- ✅ Real-time verification
- 💰 Status: "✓ Payment Confirmed" (after verification)

### UPI QR / Manual Transfer
- ✅ User provides transaction ID
- ✅ Manual admin verification
- ⏳ Status: "⏳ Awaiting Confirmation"

---

## 🔍 What Happens at Each Step

### Checkout Page
```
1. Add products to cart
2. Click "Checkout"
3. Fill: Address + Mobile
4. Select: Payment Method
5. (For UPI): Enter Transaction ID
6. Click: "Place Order"
```

### For Razorpay:
```
1. Backend creates Razorpay order
2. Redirect to payment page
3. Razorpay modal opens
4. User enters card details
5. Payment processed
6. Signature verified
7. Redirect to success page
8. Status: PAID ✓
```

### For COD/UPI:
```
1. Order created
2. Invoice generated
3. User redirected to success
4. Status: PENDING ⏳
```

---

## 📊 View Order Status

### Customer Dashboard
- Go to: http://127.0.0.1:8000/dashboard/
- See: All orders with payment status
- Download: Invoices

### Order Success Page
- Shows: Payment method & status
- Download: Your invoices
- Actions: Continue shopping, View orders

---

## 🛠️ Troubleshooting

### Issue: "Razorpay keys not configured"
**Solution**: 
1. Open `.env` file
2. Add `RAZORPAY_KEY_ID` and `RAZORPAY_KEY_SECRET`
3. Restart Django server

### Issue: "Payment signature verification failed"
**Solution**:
1. Check keys are correct in `.env`
2. Verify you're using matching test/live keys
3. Check network connectivity

### Issue: "Order not found"
**Solution**:
1. Ensure user is logged in
2. Check order was created in database
3. Verify correct user making payment

### Issue: Payment button not appearing
**Solution**:
1. Clear browser cache
2. Hard refresh (Ctrl+Shift+R on Windows)
3. Check browser console for JavaScript errors

---

## 📱 Mobile Testing

Payment gateway works on mobile devices. Test with:
- iPhone/iPad: iOS Safari
- Android: Chrome/Firefox
- Smart TV browsers

---

## 🔐 Security Checklist

- ✅ CSRF protection enabled
- ✅ HMAC SHA256 verification
- ✅ Keys stored in .env (not in code)
- ✅ HTTPS recommended for production
- ✅ Login required for payments

---

## 📈 Going to Production

1. **Get Live Keys**:
   - Visit Razorpay dashboard
   - Switch to Live mode
   - Copy live Key ID and Secret

2. **Update .env**:
   ```env
   RAZORPAY_KEY_ID=rzp_live_xxxxxxxxxxxxx
   RAZORPAY_KEY_SECRET=xxxxxxxxxxxxxxxxxxxxx
   ```

3. **Enable HTTPS**:
   - Update `SECURE_SSL_REDIRECT=True` in settings
   - Get SSL certificate (Let's Encrypt recommended)

4. **Set DEBUG=False**:
   ```env
   DJANGO_DEBUG=False
   ```
6. **Create an admin user** (run once after deploying, or let the build script do it for you):
   ```bash
   python manage.py createsuperuser
   # or use the helper:
   python create_admin.py
   # credentials can be customized via ADMIN_USERNAME and ADMIN_PASSWORD env vars
   ```

   The `build.sh` script now automatically invokes `create_admin.py`, so a superuser
   is guaranteed to exist on every deployment (default 'ayush' / 'Pass@123').
5. **Test Again**:
   - Test with small amount
   - Test refund process
   - Monitor for errors

---

## 📞 Support Resources

- [Razorpay API Docs](https://razorpay.com/docs/api/payments/)
- [Razorpay Test Cards](https://razorpay.com/docs/testing/)
- [Django Documentation](https://docs.djangoproject.com/)
- [Project README](./README.md)
- [Payment Gateway Docs](./PAYMENT_GATEWAY.md)

---

## ✨ Key Features

✅ Multiple payment methods  
✅ Secure signature verification  
✅ Real-time order status  
✅ Automatic invoice generation  
✅ Email notifications  
✅ Dashboard integration  
✅ Test & live mode support  
✅ Mobile-friendly interface  

---

**Status:** ✅ Ready to Use
**Last Updated:** February 23, 2026
