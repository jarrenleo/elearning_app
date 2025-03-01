from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model


class SearchViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.search_url = reverse("search:search")
        self.User = get_user_model()

        # Create test users
        self.user1 = self.User.objects.create_user(
            username="testuser",
            first_name="Test",
            last_name="User",
            password="password123",
            role="STUDENT",
        )

    def test_empty_query_returns_empty_results(self):
        """Test that an empty search query returns empty results"""
        response = self.client.get(self.search_url, {"query": ""})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["results"]), 0)

    def test_search_by_username(self):
        """Test searching users by username"""
        response = self.client.get(self.search_url, {"query": "testuser"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["results"]), 1)
        self.assertEqual(response.context["results"][0]["username"], "testuser")

    def test_search_by_first_name(self):
        """Test searching users by first name"""
        response = self.client.get(self.search_url, {"query": "Test"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["results"]), 1)
        self.assertEqual(response.context["results"][0]["name"], "Test User")

    def test_search_by_last_name(self):
        """Test searching users by last name"""
        response = self.client.get(self.search_url, {"query": "User"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["results"]), 1)

    def test_search_results_format(self):
        """Test that search results contain the expected fields"""
        response = self.client.get(self.search_url, {"query": "testuser"})
        result = response.context["results"][0]
        self.assertIn("name", result)
        self.assertIn("username", result)
        self.assertIn("role", result)
        self.assertEqual(result["role"], "STUDENT")  # Test capitalization
