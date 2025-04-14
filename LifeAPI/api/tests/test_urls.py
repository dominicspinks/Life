from django.test import TestCase
from django.urls import reverse, resolve
from api.views import RegisterView, LogoutView, ListItemViewSet
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


class URLTests(TestCase):
    """Test the URL configurations of the API application."""

    def test_auth_urls(self):
        """Test authentication URL patterns."""
        # Test login URL
        url = reverse('token_obtain_pair')
        self.assertEqual(url, '/api/auth/login/')
        self.assertEqual(resolve(url).func.view_class, TokenObtainPairView)

        # Test token refresh URL
        url = reverse('token_refresh')
        self.assertEqual(url, '/api/auth/login/refresh/')
        self.assertEqual(resolve(url).func.view_class, TokenRefreshView)

        # Test register URL
        url = reverse('auth_register')
        self.assertEqual(url, '/api/auth/register/')
        self.assertEqual(resolve(url).func.view_class, RegisterView)

        # Test logout URL
        url = reverse('auth_logout')
        self.assertEqual(url, '/api/auth/logout/')
        self.assertEqual(resolve(url).func.view_class, LogoutView)

    def test_module_urls(self):
        """Test module-related URL patterns."""
        # Test module types list URL
        url = reverse('moduletype-list')
        self.assertEqual(url, '/api/modules/types/')

        # Test module type detail URL
        url = reverse('moduletype-detail', args=[1])
        self.assertEqual(url, '/api/modules/types/1/')

        # Test user modules list URL
        url = reverse('user-module-list')
        self.assertEqual(url, '/api/modules/user-modules/')

        # Test user module detail URL
        url = reverse('user-module-detail', args=[1])
        self.assertEqual(url, '/api/modules/user-modules/1/')

    def test_list_urls(self):
        """Test list-related URL patterns."""
        # Test list configuration list URL
        url = reverse('configuration-list')
        self.assertEqual(url, '/api/lists/configurations/')

        # Test list configuration detail URL
        url = reverse('configuration-detail', args=[1])
        self.assertEqual(url, '/api/lists/configurations/1/')

        # Test list data list URL
        url = reverse('data-list')
        self.assertEqual(url, '/api/lists/data/')

        # Test list data detail URL
        url = reverse('data-detail', args=[1])
        self.assertEqual(url, '/api/lists/data/1/')

        # Test list items URL
        url = reverse('list-items-list', args=[1])
        self.assertEqual(url, '/api/lists/data/1/items/')

        # Test list item detail URL
        url = reverse('list-items-detail', args=[1, 2])
        self.assertEqual(url, '/api/lists/data/1/items/2/')

        # Test list configuration field URL
        url = reverse('configuration-fields-list', args=[1])
        self.assertEqual(url, '/api/lists/configurations/1/fields/')

        # Test list configuration field detail URL
        url = reverse('configuration-fields-detail', args=[1, 2])
        self.assertEqual(url, '/api/lists/configurations/1/fields/2/')

    def test_reference_urls(self):
        """Test reference data URL patterns."""
        # Test field types list URL
        url = reverse('field-type-list')
        self.assertEqual(url, '/api/reference/field-types/')

        # Test field type detail URL
        url = reverse('field-type-detail', args=[1])
        self.assertEqual(url, '/api/reference/field-types/1/')

    def test_nested_url_resolution(self):
        """Test that our nested URL structure correctly resolves."""
        # Test that a list item view resolves to the correct view class
        url = '/api/lists/data/1/items/'
        resolver = resolve(url)
        self.assertEqual(resolver.func.cls, ListItemViewSet)

        # Check that a URL with multiple segments resolves correctly
        url = '/api/lists/data/1/items/2/'
        resolver = resolve(url)
        self.assertEqual(resolver.func.cls, ListItemViewSet)
        self.assertEqual(resolver.kwargs['list_id'], '1')
        self.assertEqual(resolver.kwargs['id'], '2')