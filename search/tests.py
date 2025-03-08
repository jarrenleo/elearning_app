from django.test import TestCase
from django.urls import reverse
from accounts.models import User


class SearchViewTests(TestCase):
    def setUp(self):
        self.search_url = reverse("search:search")
        # Create test users
        self.user = User.objects.create_user(
            username="test_teacher",
            password="123456",
            first_name="Test",
            last_name="Teacher",
            email="teacher@test.com",
            role=User.Role.TEACHER,
        )

    # Test searching users by username
    def test_search_by_username(self):
        self.client.force_login(self.user)
        response = self.client.get(self.search_url, {"query": "test_teacher"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["results"]), 1)
        self.assertEqual(response.context["results"][0]["username"], "test_teacher")

    # Test searching users by first name
    def test_search_by_first_name(self):
        self.client.force_login(self.user)
        response = self.client.get(self.search_url, {"query": "Test"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["results"]), 1)
        self.assertEqual(response.context["results"][0]["name"], "Test Teacher")

    # Test searching users by last name
    def test_search_by_last_name(self):
        self.client.force_login(self.user)
        response = self.client.get(self.search_url, {"query": "Teacher"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["results"]), 1)
