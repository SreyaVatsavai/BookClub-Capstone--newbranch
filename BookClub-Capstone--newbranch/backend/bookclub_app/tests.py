# Create your tests here.
# bookclub_app/tests.py
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from .models import Book, ReadingGroup


class AuthTests(APITestCase):
    def test_check_username_available(self):
        response = self.client.get('/api/check-username/', {'username': 'noone'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('available', response.data)
        self.assertTrue(response.data['available'])

    def test_check_username_taken(self):
        User.objects.create_user('taken', password='pass123')
        response = self.client.get('/api/check-username/', {'username': 'taken'})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.data['available'])

    def test_register_success(self):
        response = self.client.post('/api/auth/register/', {
            'username': 'testuser',
            'password': 'StrongPass1'
        })
        self.assertEqual(response.status_code, 201)
        self.assertIn('message', response.data)

    def test_register_short_username(self):
        response = self.client.post('/api/auth/register/', {
            'username': 'ab',
            'password': 'StrongPass1'
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn('username', response.data)

    def test_register_weak_password(self):
        # Password missing uppercase / digits or too short
        response = self.client.post('/api/auth/register/', {
            'username': 'newuser',
            'password': 'abc'
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn('password', response.data)

    def test_login(self):
        User.objects.create_user('testuser', password='testpass123')
        response = self.client.post('/api/auth/login/', {
            'username': 'testuser',
            'password': 'testpass123'
        })
        # Successful login should return serialized user (200)
        self.assertEqual(response.status_code, 200)


class BookTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user('user', password='pass')
        Book.objects.create(
            title="Test Book", author="Author", genre="Fiction",
            description="...", total_pages=100, total_chapters=10
        )

    def test_book_list_requires_auth(self):
        # Unauthenticated should be denied
        response = self.client.get('/api/books/')
        self.assertIn(response.status_code, (401, 403))

    def test_book_list_authenticated(self):
        self.client.login(username='user', password='pass')
        response = self.client.get('/api/books/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_book_detail_not_found(self):
        self.client.login(username='user', password='pass')
        response = self.client.get('/api/books/9999/')
        self.assertEqual(response.status_code, 404)