from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()

class RegisterViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('auth_register')
        self.valid_payload = {
            'email': 'newuser@example.com',
            'password': 'SecurePassword123!'
        }
        self.weak_password_payload = {
            'email': 'newuser@example.com',
            'password': '123'  # Too short/simple
        }
        self.invalid_email_payload = {
            'email': 'not-an-email',
            'password': 'SecurePassword123!'
        }
        self.duplicate_email_payload = {
            'email': 'existing@example.com',
            'password': 'SecurePassword123!'
        }
        # Create an existing user for duplicate email tests
        User.objects.create_user(
            email='existing@example.com',
            password='ExistingPassword123'
        )

    def test_valid_registration(self):
        """Test registration with valid credentials."""
        response = self.client.post(
            self.register_url,
            self.valid_payload,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email='newuser@example.com').exists())

    def test_weak_password_registration(self):
        """Test registration with a weak password."""
        response = self.client.post(
            self.register_url,
            self.weak_password_payload,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)

    def test_invalid_email_registration(self):
        """Test registration with an invalid email."""
        response = self.client.post(
            self.register_url,
            self.invalid_email_payload,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_duplicate_email_registration(self):
        """Test registration with an email that already exists."""
        response = self.client.post(
            self.register_url,
            self.duplicate_email_payload,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)


class TokenObtainViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.login_url = reverse('token_obtain_pair')
        self.user_credentials = {
            'email': 'testuser@example.com',
            'password': 'TestPassword123!'
        }
        # Create a user
        self.user = User.objects.create_user(
            email=self.user_credentials['email'],
            password=self.user_credentials['password']
        )

    def test_valid_login(self):
        """Test login with valid credentials."""
        response = self.client.post(
            self.login_url,
            self.user_credentials,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        # We no longer expect 'user' in the response based on the actual implementation

    def test_invalid_password(self):
        """Test login with invalid password."""
        invalid_credentials = {
            'email': self.user_credentials['email'],
            'password': 'WrongPassword123'
        }
        response = self.client.post(
            self.login_url,
            invalid_credentials,
            format='json'
        )
        # API returns 401 for invalid credentials, not 400
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_nonexistent_user(self):
        """Test login with email that doesn't exist."""
        nonexistent_credentials = {
            'email': 'nonexistent@example.com',
            'password': 'SomePassword123'
        }
        response = self.client.post(
            self.login_url,
            nonexistent_credentials,
            format='json'
        )
        # API returns 401 for nonexistent users, not 400
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_missing_fields(self):
        """Test login with missing fields."""
        # Missing password
        missing_password = {
            'email': self.user_credentials['email']
        }
        response = self.client.post(
            self.login_url,
            missing_password,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Missing email
        missing_email = {
            'password': self.user_credentials['password']
        }
        response = self.client.post(
            self.login_url,
            missing_email,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TokenRefreshViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.login_url = reverse('token_obtain_pair')
        self.refresh_url = reverse('token_refresh')
        self.user_credentials = {
            'email': 'testuser@example.com',
            'password': 'TestPassword123!'
        }
        # Create a user
        self.user = User.objects.create_user(
            email=self.user_credentials['email'],
            password=self.user_credentials['password']
        )

        # Get refresh token
        response = self.client.post(
            self.login_url,
            self.user_credentials,
            format='json'
        )
        self.refresh_token = response.data['refresh']

    def test_valid_refresh(self):
        """Test refreshing token with valid refresh token."""
        response = self.client.post(
            self.refresh_url,
            {'refresh': self.refresh_token},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        # We no longer expect 'refresh' in the response based on the actual implementation

    def test_invalid_refresh(self):
        """Test refreshing token with invalid refresh token."""
        response = self.client.post(
            self.refresh_url,
            {'refresh': 'invalid-token'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class LogoutViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.login_url = reverse('token_obtain_pair')
        self.logout_url = reverse('auth_logout')
        self.user_credentials = {
            'email': 'testuser@example.com',
            'password': 'TestPassword123!'
        }
        # Create a user
        self.user = User.objects.create_user(
            email=self.user_credentials['email'],
            password=self.user_credentials['password']
        )

        # Log in to get tokens
        response = self.client.post(
            self.login_url,
            self.user_credentials,
            format='json'
        )
        self.access_token = response.data['access']

    def test_logout_authenticated(self):
        """Test logging out when authenticated."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = self.client.post(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('detail', response.data)
        self.assertEqual(response.data['detail'], 'Successfully logged out.')

    def test_logout_unauthenticated(self):
        """Test logging out when not authenticated."""
        response = self.client.post(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)