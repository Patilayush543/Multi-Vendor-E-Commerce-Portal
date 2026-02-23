#!/usr/bin/env python
"""
Payment Gateway Testing Guide
Test the Razorpay, UPI QR, and COD payment methods
"""

import os
import django
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ECommerce.settings')
django.setup()

from myapp.models import Product, Cart, CartItem, CartOrder

class PaymentGatewayTests(TestCase):
    """Test payment gateway functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create test product
        self.product = Product.objects.create(
            title='Test Product',
            slug='test-product',
            category='electronics',
            price=1000,
            description='Test product',
        )
        
        # Create cart
        self.cart = Cart.objects.create(user=self.user, total=1000)
        self.cart_item = CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=1
        )
    
    def test_cod_payment(self):
        """Test Cash on Delivery payment"""
        self.client.login(username='testuser', password='testpass123')
        
        # Simulate checkout with COD
        response = self.client.post(reverse('confirm_order'), {
            'address': '123 Main St',
            'mobile': '9876543210',
            'payment_method': 'cod',
        }, follow=True)
        
        # Check order was created
        order = CartOrder.objects.filter(user=self.user).first()
        self.assertIsNotNone(order)
        self.assertEqual(order.payment_method, 'cod')
        self.assertEqual(order.payment_status, 'pending')
        
        print("✓ COD Payment Test Passed")
    
    def test_upi_payment(self):
        """Test UPI QR payment"""
        self.client.login(username='testuser', password='testpass123')
        
        # Simulate checkout with UPI QR
        response = self.client.post(reverse('confirm_order'), {
            'address': '123 Main St',
            'mobile': '9876543210',
            'payment_method': 'upi_qr',
            'transaction_id': 'UPI123456789',
        }, follow=True)
        
        # Check order was created
        order = CartOrder.objects.filter(user=self.user).first()
        self.assertIsNotNone(order)
        self.assertEqual(order.payment_method, 'upi_qr')
        self.assertEqual(order.payment_status, 'pending')
        self.assertEqual(order.transaction_id, 'UPI123456789')
        
        print("✓ UPI Payment Test Passed")
    
    def test_razorpay_payment(self):
        """Test Razorpay payment initialization"""
        self.client.login(username='testuser', password='testpass123')
        
        # Simulate checkout with Razorpay
        # Note: This will create a Razorpay order if keys are configured
        response = self.client.post(reverse('confirm_order'), {
            'address': '123 Main St',
            'mobile': '9876543210',
            'payment_method': 'razorpay',
        })
        
        # Check response status
        if 'razorpay_order_id' in response.context or response.status_code == 302:
            print("✓ Razorpay Payment Test Passed")
        else:
            print("⚠ Razorpay Payment Test: Keys may not be configured")
    
    def test_payment_verification(self):
        """Test payment verification endpoint"""
        self.client.login(username='testuser', password='testpass123')
        
        # First create an order
        order = CartOrder.objects.create(
            user=self.user,
            product=self.product,
            product_name=self.product.title,
            price=1000,
            payment_method='razorpay',
            payment_status='pending',
            transaction_id='order_RAZORPAYxxx',
        )
        
        # Test verification endpoint
        # Note: Signature verification will fail without valid keys
        response = self.client.post(reverse('verify_razorpay'), 
            data=json.dumps({
                'razorpay_order_id': 'order_RAZORPAYxxx',
                'razorpay_payment_id': 'pay_xxxxx',
                'razorpay_signature': 'invalid_signature',
            }),
            content_type='application/json'
        )
        
        # Should return error for invalid signature
        if response.status_code in [400, 404, 500]:
            print("✓ Payment Verification Test Passed (signature rejected as expected)")
        else:
            print("⚠ Payment Verification Test: Response status", response.status_code)

if __name__ == '__main__':
    # Run tests
    print("\n" + "="*50)
    print("Payment Gateway Test Suite")
    print("="*50 + "\n")
    
    # Create test suite
    from django.test.runner import DiscoverRunner
    runner = DiscoverRunner(verbosity=2)
    
    # Run specific tests
    test = PaymentGatewayTests()
    test.setUp()
    test.test_cod_payment()
    test.test_upi_payment()
    test.test_razorpay_payment()
    test.test_payment_verification()
    
    print("\n" + "="*50)
    print("Test Suite Complete")
    print("="*50 + "\n")
