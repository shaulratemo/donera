from django.contrib.auth import get_user_model
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient

from organizations.models import Organization
from .models import UserProfile


User = get_user_model()


class UserProfileSignalTests(TestCase):
	def test_user_creation_creates_profile(self):
		user = User.objects.create_user(
			email="donor@example.com",
			password="testpass123",
			first_name="Donor",
			last_name="User",
		)

		self.assertTrue(UserProfile.objects.filter(user=user).exists())

	def test_saving_user_without_profile_recreates_it(self):
		user = User.objects.create_user(
			email="admin@example.com",
			password="testpass123",
			role="ADMIN",
			first_name="Admin",
			last_name="User",
		)
		UserProfile.objects.filter(user=user).delete()

		user.phone_number = "254700000000"
		user.save()

		self.assertTrue(UserProfile.objects.filter(user=user).exists())


class UserRoleSerializerBehaviorTests(TestCase):
	def setUp(self):
		self.client = APIClient()

	def test_registration_accepts_role_from_payload(self):
		payload = {
			"email": "org-admin@example.com",
			"password": "testpass123",
			"first_name": "Org",
			"last_name": "Admin",
			"role": "ORGANIZATION",
		}

		response = self.client.post("/api/users/register/", payload, format="json")

		self.assertEqual(response.status_code, 201)
		user = User.objects.get(email="org-admin@example.com")
		self.assertEqual(user.role, "ORGANIZATION")

	def test_profile_update_cannot_change_role(self):
		user = User.objects.create_user(
			email="donor1@example.com",
			password="testpass123",
			role="DONOR",
			first_name="Donor",
			last_name="One",
		)
		self.client.force_authenticate(user=user)

		response = self.client.patch(
			"/api/users/me/",
			{"role": "ADMIN"},
			format="json",
		)

		self.assertEqual(response.status_code, 200)
		user.refresh_from_db()
		self.assertEqual(user.role, "DONOR")


class JwtCustomClaimsTests(TestCase):
	def setUp(self):
		self.client = APIClient()

	def test_login_response_includes_role_and_has_organization_false(self):
		User.objects.create_user(
			email="donor-login@example.com",
			password="testpass123",
			role="DONOR",
		)

		response = self.client.post(
			"/api/users/login/",
			{"email": "donor-login@example.com", "password": "testpass123"},
			format="json",
		)

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.data["role"], "DONOR")
		self.assertFalse(response.data["has_organization"])

	def test_login_response_includes_role_and_has_organization_true(self):
		user = User.objects.create_user(
			email="org-login@example.com",
			password="testpass123",
			role="ORGANIZATION",
		)
		Organization.objects.create(
			owner=user,
			name="Test Org",
			description="Test Description",
			registration_number="REG-12345",
			kra_pin="A123456789B",
			tcc_number="TCC-12345",
			tcc_document=SimpleUploadedFile(
				"tcc.pdf",
				b"test",
				content_type="application/pdf",
			),
		)

		response = self.client.post(
			"/api/users/login/",
			{"email": "org-login@example.com", "password": "testpass123"},
			format="json",
		)

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.data["role"], "ORGANIZATION")
		self.assertTrue(response.data["has_organization"])
