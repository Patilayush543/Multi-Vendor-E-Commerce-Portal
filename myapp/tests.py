from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

from .models import CartOrder, Product


class AdminLoginTest(TestCase):
    """Ensure the /admin/ interface is reachable and accepts our default credentials.

    This helps catch issues with ALLOWED_HOSTS/CSRF and user provisioning in CI or
    when deployed to Render.  The test creates a superuser if one does not exist.
    """

    def setUp(self):
        User = get_user_model()
        if not User.objects.filter(username='ayush').exists():
            # password is intentionally weak; only used for automated tests
            User.objects.create_superuser('ayush', 'admin@example.com', 'Pass@123')
        self.client = Client()

    def test_admin_login(self):
        self.assertTrue(self.client.login(username='ayush', password='Pass@123'))
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 200)


class SessionCartTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.product = Product.objects.create(
            title='Leather Jacket',
            brand='PatilApx',
            price='199.99',
            description='Premium jacket',
            category='fashion',
            image_url='https://example.com/jacket.jpg',
            stock_count=10,
        )
        self.user = get_user_model().objects.create_user(
            username='cartuser',
            email='cart@example.com',
            password='Pass@123',
        )

    def test_anonymous_add_to_cart_uses_session(self):
        response = self.client.get(reverse('add_to_cart', args=[self.product.id]), secure=True)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers['Location'], reverse('auth'))
        self.assertFalse(CartOrder.objects.exists())
        self.assertNotIn('guest_cart', self.client.session)

    def test_login_merges_session_cart_into_pending_orders(self):
        session = self.client.session
        session['guest_cart'] = {str(self.product.id): 3}
        session.save()

        response = self.client.post(reverse('login_user'), {
            'email': 'cart@example.com',
            'password': 'Pass@123',
        }, secure=True)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers['Location'], '/')
        order = CartOrder.objects.get(user=self.user, product=self.product, status='pending')
        self.assertEqual(order.quantity, 3)
        self.assertNotIn('guest_cart', self.client.session)

    def test_checkout_redirects_anonymous_user_to_auth(self):
        response = self.client.get(reverse('checkout'), secure=True)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers['Location'], reverse('auth'))
