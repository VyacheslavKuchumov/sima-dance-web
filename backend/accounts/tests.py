from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase


User = get_user_model()


class AccountsApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='profile-user',
            password='StartPass123!',
            email='old@example.com',
            first_name='Old',
            last_name='Name',
        )
        token_response = self.client.post(
            '/api/accounts/token/',
            {'username': 'profile-user', 'password': 'StartPass123!'},
            format='json',
        )
        self.assertEqual(token_response.status_code, status.HTTP_200_OK)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {token_response.data['access']}"
        )

    def test_patch_me_updates_profile_fields(self):
        response = self.client.patch(
            '/api/accounts/me/',
            {
                'email': 'new@example.com',
                'first_name': 'New',
                'last_name': 'Person',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'new@example.com')
        self.assertEqual(self.user.first_name, 'New')
        self.assertEqual(self.user.last_name, 'Person')

    def test_change_password_requires_current_password(self):
        response = self.client.post(
            '/api/accounts/change-password/',
            {
                'current_password': 'WrongPass123!',
                'new_password': 'BetterPass456!',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('StartPass123!'))

    def test_change_password_updates_password(self):
        response = self.client.post(
            '/api/accounts/change-password/',
            {
                'current_password': 'StartPass123!',
                'new_password': 'BetterPass456!',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('BetterPass456!'))
        self.assertFalse(self.user.check_password('StartPass123!'))
