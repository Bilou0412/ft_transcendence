from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient,APITestCase
from django.db import connection
from django.contrib.auth.models import User
from django.core import mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from termcolor import colored
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken , BlacklistedToken

class SecurityTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='Testpass123@@',
            is_active=True
        )

    def test_xss_protection(self):
        # Vérifiez que les données saisies par l'utilisateur sont correctement échappées
        url = reverse('signup')
        data = {
            'username': '<script>alert("XSS")</script>',
            'email': 'xss@example.com',
            'password': 'xsspass123',
            'password2': 'xsspass123'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        print(colored("XSS protection test passed", "green"))

    def test_token_security(self):
        # Vérifiez que les jetons d'authentification sont correctement sécurisés
        url = reverse('token_validate')
        data = {'token': 'invalid_token'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        print(colored("Token security test passed", "green"))

    def test_dos_protection(self):
        # Vérifiez que l'application peut gérer un grand nombre de requêtes simultanées
        url = reverse('login')
        data = {'username': 'testuser', 'password': 'Testpass123@@'}
        for _ in range(100):  # Simuler un grand nombre de requêtes
            response = self.client.post(url, data)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        print(colored("DoS protection test passed", "green"))

    def test_impersonation_protection(self):
        # Vérifiez que les jetons d'authentification ne peuvent pas être falsifiés
        url = reverse('token_validate')
        data = {'token': 'falsified_token'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        print(colored("Impersonation protection test passed", "green"))


class AuthenticationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='Testpass123@@',
            is_active=True
        )
        self.inactive_user = User.objects.create_user(
            username='inactiveuser',
            email='inactive@example.com',
            password='inactivepass123',
            is_active=False
        )

    def test_login_success(self):
        url = reverse('login')
        data = {'username': 'testuser', 'password': 'Testpass123@@'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('refresh', response.data)
        self.assertIn('access', response.data)
        print(colored("Login successful", "green"))

    def test_login_with_email(self):
        url = reverse('login')
        data = {'username': 'testuser@example.com', 'password': 'Testpass123@@'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print(colored("Login with email successful", "green"))

    def test_login_invalid_credentials(self):
        url = reverse('login')
        data = {'username': 'testuser', 'password': 'wrongpass'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        print(colored("Login with invalid credentials handled correctly", "green"))

    def test_login_inactive_user(self):
        url = reverse('login')
        data = {'username': 'inactiveuser', 'password': 'inactivepass123'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        print(colored("Login for inactive user handled correctly", "green"))

    def test_signup_success(self):
        url = reverse('signup')
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'Mewpass123@@',
            'password2': 'Mewpass123@@'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Vérification de votre adresse e-mail', mail.outbox[0].subject)
        print(colored("Signup successful", "green"))

    def test_email_verification_success(self):
        user = User.objects.create_user(username='verifyuser', email='verify@example.com', password='verifypass123', is_active=False)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        url = reverse('email_verification', kwargs={'uidb64': uid, 'token': token})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertTrue(user.is_active)
        print(colored("Email verification successful", "green"))

    def test_refresh_token(self):
        login_url = reverse('login')
        login_data = {'username': 'testuser', 'password': 'Testpass123@@'}
        login_response = self.client.post(login_url, login_data)
        refresh_token = login_response.data['refresh']

        url = reverse('token_refresh')
        data = {'refresh': refresh_token}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        print(colored("Token refresh successful", "green"))

    def test_reset_password_request(self):
        url = reverse('password_reset_request')
        data = {'email': 'testuser@example.com'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Password Reset Request', mail.outbox[0].subject)
        print(colored("Password reset request handled successfully", "green"))

    def test_reset_password_confirm(self):
        user = self.user
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        url = reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
        data = {'new_password': 'Newpassword123@@'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertTrue(user.check_password('Newpassword123@@'))
        print(colored("Password reset confirmed", "green"))

    def test_change_password(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('change_password')
        data = {'old_password': 'Testpass123@@', 'new_password': 'Changedpass123@@'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('Changedpass123@@'))
        print(colored("Password changed successfully", "green"))

    def test_logout_successful(self):
        """
        Test si la déconnexion réussit lorsque le refresh token est valide.
        """
        login_url = reverse('login')
        login_data = {'username': 'testuser', 'password': 'Testpass123@@'}
        login_response = self.client.post(login_url, login_data)
        refresh_token = login_response.data['refresh']
        access_token = login_response.data['access']

        # Authentifiez l'utilisateur avec le token d'accès
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

        url = reverse('logout')
        response = self.client.post(url, {'refresh': refresh_token})
        self.assertEqual(response.status_code, status.HTTP_205_RESET_CONTENT)
        self.assertEqual(response.data['detail'], "Successfully logged out.")
        outstanding_token = OutstandingToken.objects.get(token=refresh_token)
        self.assertTrue(BlacklistedToken.objects.filter(token=outstanding_token).exists())
        print(colored("Logout successful", "green"))

    def test_logout_token_already_blacklisted_or_invalid(self):
        """
        Test si la déconnexion échoue lorsque le refresh token est déjà blacklisté ou invalide.
        """
        login_url = reverse('login')
        login_data = {'username': 'testuser', 'password': 'Testpass123@@'}
        login_response = self.client.post(login_url, login_data)
        refresh_token = login_response.data['refresh']
        access_token = login_response.data['access']

        # Blacklist le token d'abord
        outstanding_token = OutstandingToken.objects.get(token=refresh_token)
        BlacklistedToken.objects.create(token=outstanding_token)

        # Authentifiez l'utilisateur avec le token d'accès
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

        # Tente de se déconnecter avec le même token
        url = reverse('logout')
        response = self.client.post(url, {'refresh': refresh_token})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], "Token already blacklisted or invalid.")
        print(colored("Logout with blacklisted token handled correctly", "green"))

    def test_logout_no_token_provided(self):
        """
        Test si la déconnexion échoue lorsque le token n'est pas fourni.
        """
        login_url = reverse('login')
        login_data = {'username': 'testuser', 'password': 'Testpass123@@'}
        login_response = self.client.post(login_url, login_data)
        access_token = login_response.data['access']

        # Authentifiez l'utilisateur avec le token d'accès
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

        url = reverse('logout')
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], "Refresh token is required.")
        print(colored("Logout without token handled correctly", "green"))

class SQLInjectionTestCase(APITestCase):
    def test_sql_injection(self):
        # Payload tentant une injection SQL dans le champ username
        malicious_username = "'; DROP TABLE auth_user; --"
        payload = {
            'username': malicious_username,
            'password': 'Password123@@',
            'password2': 'Password123@@',
            'email': "test@example.com"
        }

        # Compter le nombre d'utilisateurs avant la tentative d'injection
        initial_user_count = User.objects.count()

        # Envoyer la requête POST
        response = self.client.post(reverse('signup'), payload)

        # Vérifier que la réponse est une erreur de validation
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)   

        # Vérifier que le nombre d'utilisateurs n'a pas changé, donc l'injection a échoué
        self.assertEqual(User.objects.count(), initial_user_count)

        # Vérifier que la table des utilisateurs existe toujours
        with connection.cursor() as cursor:
            cursor.execute("SELECT to_regclass('auth_user');")
            result = cursor.fetchone()
            self.assertIsNotNone(result[0])  # La table doit exister