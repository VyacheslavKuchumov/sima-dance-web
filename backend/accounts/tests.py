from django.core.management import call_command
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from .group_defaults import DEFAULT_SIGNUP_GROUP_NAMES, LEGACY_DEFAULT_GROUP_NAME
from .models import UserGroup, UserProfile


User = get_user_model()


class AccountsApiTests(APITestCase):
    def setUp(self):
        self.group = UserGroup.objects.create(name='Dance group')
        self.other_group = UserGroup.objects.create(name='Advanced group')
        self.user = User.objects.create_user(
            username='profile-user',
            password='StartPass123!',
            email='old@example.com',
            first_name='Old',
            last_name='Name',
        )
        self.profile = UserProfile.objects.create(
            user=self.user,
            group=self.group,
            full_name='Старое ФИО',
            child_full_name='Старое ФИО ребенка',
        )
        self.superuser = User.objects.create_superuser(
            username='root-user',
            password='RootPass123!',
            email='root@example.com',
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

    def test_signup_groups_endpoint_lists_groups(self):
        extra_group = UserGroup.objects.create(name='Another group')

        response = self.client.get('/api/accounts/signup-groups/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            [item['name'] for item in response.data],
            DEFAULT_SIGNUP_GROUP_NAMES + [self.other_group.name, extra_group.name, self.group.name],
        )

    def test_set_groups_command_removes_unused_legacy_group(self):
        UserGroup.objects.get_or_create(name=LEGACY_DEFAULT_GROUP_NAME)

        call_command('set_groups')

        self.assertFalse(UserGroup.objects.filter(name=LEGACY_DEFAULT_GROUP_NAME).exists())
        self.assertEqual(
            UserGroup.objects.filter(name__in=DEFAULT_SIGNUP_GROUP_NAMES).count(),
            len(DEFAULT_SIGNUP_GROUP_NAMES),
        )

    def test_set_groups_command_keeps_used_legacy_group(self):
        legacy_group = UserGroup.objects.create(name=LEGACY_DEFAULT_GROUP_NAME)
        legacy_user = User.objects.create_user(
            username='legacy-user',
            password='StartPass123!',
        )
        UserProfile.objects.create(
            user=legacy_user,
            group=legacy_group,
            full_name='Пользователь Наследия',
            child_full_name='Ребенок Наследия',
        )

        call_command('set_groups')

        self.assertTrue(UserGroup.objects.filter(name=LEGACY_DEFAULT_GROUP_NAME).exists())

    def test_signup_creates_user_profile_with_group(self):
        response = self.client.post(
            '/api/accounts/signup/',
            {
                'username': 'new-user',
                'password': 'StartPass123!',
                'group': self.group.id,
                'full_name': 'Иван Иванов',
                'child_full_name': 'Петя Иванов',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(username='new-user')
        profile = UserProfile.objects.get(user=user)

        self.assertEqual(profile.group_id, self.group.id)
        self.assertEqual(profile.full_name, 'Иван Иванов')
        self.assertEqual(profile.child_full_name, 'Петя Иванов')

    def test_patch_me_updates_profile_fields(self):
        response = self.client.patch(
            '/api/accounts/me/',
            {
                'email': 'new@example.com',
                'first_name': 'New',
                'last_name': 'Person',
                'group': self.other_group.id,
                'full_name': 'Новое ФИО',
                'child_full_name': 'Новое ФИО ребенка',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.profile.refresh_from_db()
        self.assertEqual(self.user.email, 'new@example.com')
        self.assertEqual(self.user.first_name, 'New')
        self.assertEqual(self.user.last_name, 'Person')
        self.assertEqual(self.profile.group_id, self.other_group.id)
        self.assertEqual(self.profile.full_name, 'Новое ФИО')
        self.assertEqual(self.profile.child_full_name, 'Новое ФИО ребенка')

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

    def test_me_endpoint_returns_superuser_flag(self):
        response = self.client.get('/api/accounts/me/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['is_superuser'])

    def test_admin_users_endpoint_requires_superuser(self):
        response = self.client.get('/api/accounts/admin/users/')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_create_user_endpoint_requires_superuser(self):
        response = self.client.post(
            '/api/accounts/admin/users/',
            {
                'username': 'created-by-admin',
                'password': 'StartPass123!',
                'group': self.group.id,
                'full_name': 'Админ Создал',
                'child_full_name': 'Ребенок Админа',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_impersonation_endpoint_requires_superuser(self):
        response = self.client.post(
            '/api/accounts/admin/impersonate/',
            {'user_id': self.superuser.id},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_reset_password_endpoint_requires_superuser(self):
        response = self.client.post(
            '/api/accounts/admin/reset-password/',
            {'user_id': self.user.id},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_superuser_can_list_all_users_for_admin_panel(self):
        token_response = self.client.post(
            '/api/accounts/token/',
            {'username': 'root-user', 'password': 'RootPass123!'},
            format='json',
        )
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {token_response.data['access']}"
        )

        response = self.client.get('/api/accounts/admin/users/', {'search': 'profile'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['username'], 'profile-user')
        self.assertIn('bookings_count', response.data[0])

    def test_superuser_can_create_user_from_admin_panel(self):
        token_response = self.client.post(
            '/api/accounts/token/',
            {'username': 'root-user', 'password': 'RootPass123!'},
            format='json',
        )
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {token_response.data['access']}"
        )

        response = self.client.post(
            '/api/accounts/admin/users/',
            {
                'username': 'created-by-admin',
                'password': 'StartPass123!',
                'group': self.other_group.id,
                'full_name': 'Админ Создал',
                'child_full_name': 'Ребенок Админа',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['username'], 'created-by-admin')
        self.assertEqual(response.data['profile']['group']['id'], self.other_group.id)
        self.assertEqual(response.data['profile']['full_name'], 'Админ Создал')
        self.assertEqual(response.data['profile']['child_full_name'], 'Ребенок Админа')
        self.assertEqual(response.data['bookings_count'], 0)

        user = User.objects.get(username='created-by-admin')
        self.assertTrue(user.check_password('StartPass123!'))
        self.assertEqual(user.profile.group_id, self.other_group.id)

    def test_superuser_can_impersonate_user(self):
        token_response = self.client.post(
            '/api/accounts/token/',
            {'username': 'root-user', 'password': 'RootPass123!'},
            format='json',
        )
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {token_response.data['access']}"
        )

        response = self.client.post(
            '/api/accounts/admin/impersonate/',
            {'user_id': self.user.id},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user']['id'], self.user.id)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {response.data['access']}"
        )
        me_response = self.client.get('/api/accounts/me/')

        self.assertEqual(me_response.status_code, status.HTTP_200_OK)
        self.assertEqual(me_response.data['id'], self.user.id)
        self.assertFalse(me_response.data['is_superuser'])

    def test_superuser_can_reset_user_password(self):
        token_response = self.client.post(
            '/api/accounts/token/',
            {'username': 'root-user', 'password': 'RootPass123!'},
            format='json',
        )
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {token_response.data['access']}"
        )

        response = self.client.post(
            '/api/accounts/admin/reset-password/',
            {'user_id': self.user.id},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user']['id'], self.user.id)
        self.assertEqual(response.data['user']['username'], self.user.username)
        self.assertEqual(len(response.data['generated_password']), 8)
        self.assertTrue(response.data['generated_password'].isalnum())
        self.assertTrue(any(char.isalpha() for char in response.data['generated_password']))
        self.assertTrue(any(char.isdigit() for char in response.data['generated_password']))

        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(response.data['generated_password']))
        self.assertFalse(self.user.check_password('StartPass123!'))

    def test_superuser_cannot_impersonate_inactive_user(self):
        inactive_user = User.objects.create_user(
            username='inactive-user',
            password='StartPass123!',
            is_active=False,
        )
        token_response = self.client.post(
            '/api/accounts/token/',
            {'username': 'root-user', 'password': 'RootPass123!'},
            format='json',
        )
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {token_response.data['access']}"
        )

        response = self.client.post(
            '/api/accounts/admin/impersonate/',
            {'user_id': inactive_user.id},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('user_id', response.data)
