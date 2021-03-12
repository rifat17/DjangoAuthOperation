from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

User = get_user_model()
from rest_framework import status


# Create your tests here.

def createUser(username='testuser1', email='testuser1@test.com', password='12345678', address=None):
    return User.objects.create_user(
        username=username,
        email=email,
        password=password,
        address=address
    )


class AccountTest(APITestCase):
    def setUp(self) -> None:
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.users = reverse('users')

    def test_create_user(self):
        data = {
            'username': 'testuser2',
            'email': 'testuser2@test.com',
            'password': '12345678',
            'confirm_password': '12345678',
            'address': 'Cumilla',
        }

        createUser()
        response = self.client.post(self.register_url, data=data)
        # print(User.objects.all())

        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['username'], data['username'])
        self.assertEqual(response.data['email'], data['email'])
        self.assertEqual(response.data['address'], data['address'])
        self.assertNotEqual(response.data['address'], 'Comilla')
        self.assertFalse('password' in response.data)

    def test_create_user_with_short_password(self):
        createUser()
        data = {
            'username': 'test',
            'email': 'test@test.com',
            'password': '',
        }

        response = self.client.post(self.register_url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(len(response.data['password']), 1)

    def test_create_user_with_preexisting_username(self):
        createUser()
        data = {
            'username': 'testuser1',
            'email': 'testuser1@test.com',
            'password': '12345678',
        }

        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(len(response.data['username']), 1)

    def test_create_user_with_preexisting_email(self):
        createUser()
        data = {
            'username': 'testuser2',
            'email': 'testuser1@test.com',
            'password': 'testuser'
        }

        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(len(response.data['email']), 1)

    def test_create_user_with_invalid_email(self):
        createUser()
        data = {
            'username': 'foobarbaz',
            'email': 'testing',
            'passsword': 'foobarbaz'
        }

        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(len(response.data['email']), 1)

    def test_create_user_with_no_email(self):
        createUser()
        data = {
            'username': 'foobar',
            'email': '',
            'password': 'foobarbaz'
        }

        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(len(response.data['email']), 1)

    def test_login_success(self):
        createUser()
        data = {
            'email': 'testuser1@test.com',
            'password': '12345678'
        }

        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, 'token')
        self.assertContains(response, 'email')

    def test_login_fail(self):
        createUser()
        data = {
            'email': 'testuser1@test.com',
            'password': '12345679'
        }

        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # TODO: check if token passed when login failed

    def test_invalid_user_login_fail(self):
        data = {
            'email': 'testuser@test.com',
            'password': '12345679'
        }

        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # TODO: check if token passed when login failed

    def test_get_auth_token(self):
        reg_data = {
            'username': 'tokenuser',
            'email': 'tokenuser@test.com',
            'password': '12345678',
            'address': 'Cumilla',
        }
        login_data = {
            'email': 'tokenuser@test.com',
            'password': '12345678'
        }

        createUser(username='tokenuser', email='tokenuser@test.com', password='12345678')
        response = self.client.post(self.login_url, data=login_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, 'token')

    def test_get_all_user_with_valid_token(self):

        login_data = {
            'email': 'tokenuser@test.com',
            'password': '12345678'
        }
        createUser()
        createUser("testuser2", "testuser2@test.com", "12345678", "Cumilla")
        createUser("tokenuser", "tokenuser@test.com", "12345678", "Cumilla")

        response = self.client.post(self.login_url, data=login_data)
        # print(response.data['token'])
        token = response.data['token']
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        response = client.get(self.users)
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    def test_get_404_without_valid_token(self):

        login_data = {
            'email': 'tokenuser@test.com',
            'password': '12345678'
        }
        createUser()
        createUser("testuser2", "testuser2@test.com", "12345678", "Cumilla")
        createUser("tokenuser", "tokenuser@test.com", "12345678", "Cumilla")

        response = self.client.post(self.login_url, data=login_data)
        # print(response.data['token'])
        token = response.data['token']
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + 'token')
        response = client.get(self.users)
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        print(response.data)
        self.assertEqual(len(response.data), 1)