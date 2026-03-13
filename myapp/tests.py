from django.test import TestCase, Client
from django.contrib.auth import get_user_model


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
