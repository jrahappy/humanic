from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class AccountsTestCase(TestCase):
    def setUp(self):
        # Create a user for testing
        self.user = User.objects.create_user(
            username="testuser", password="testpassword", email="testuser@example.com"
        )

    def test_user_registration(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "newuser",
                "password1": "newpassword",
                "password2": "newpassword",
                "email": "newuser@example.com",
            },
        )
        self.assertEqual(
            response.status_code, 302
        )  # Redirect after successful registration
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_user_login(self):
        response = self.client.post(
            reverse("login"), {"username": "testuser", "password": "testpassword"}
        )
        self.assertEqual(response.status_code, 302)  # Redirect after successful login
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_profile_update(self):
        self.client.login(username="testuser", password="testpassword")
        response = self.client.post(
            reverse("profile_update"),
            {"username": "updateduser", "email": "updateduser@example.com"},
        )
        self.assertEqual(
            response.status_code, 302
        )  # Redirect after successful profile update
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, "updateduser")
        self.assertEqual(self.user.email, "updateduser@example.com")
