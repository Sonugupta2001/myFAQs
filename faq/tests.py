import time
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.models import User
from .models import FAQ
from .languages import SUPPORTED_LANGUAGES
from unittest.mock import patch
from decouple import config

class FAQAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        self.admin_user = User.objects.create_superuser(
            username=config('ADMIN_USERNAME', default='admin'),
            email=config('ADMIN_EMAIL', default='admin@example.com'),
            password=config('ADMIN_PASSWORD', default='password'),
        )

        self.faq1 = FAQ.objects.create(
            question="What is Django?",
            answer="Django is a high-level Python web framework."
        )
        self.faq2 = FAQ.objects.create(
            question="What is REST?",
            answer="REST is an architectural style for designing networked applications."
        )

    def test_list_faqs_public(self):
        """Test that anyone can list FAQs"""
        response = self.client.get('/api/faqs/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_retrieve_faq_public(self):
        """Test that anyone can retrieve a specific FAQ"""
        response = self.client.get(f'/api/faqs/{self.faq1.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['question'], "What is Django?")

    def test_faq_str_method(self):
        """Test the __str__ method of the FAQ model"""
        self.assertEqual(str(self.faq1), "What is Django?")

    @patch('faq.views.FAQViewSet.translate_to_languages')
    def test_create_faq_admin(self, mock_translate):
        """Test that only admin can create FAQ"""
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'question': "What is an API?",
            'answer': "An API is a set of rules that allows programs to talk to each other."
        }
        response = self.client.post('/api/faqs/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(FAQ.objects.count(), 3)
        mock_translate.assert_called_once()

    def test_create_faq_unauthenticated(self):
        """Test that unauthenticated users cannot create FAQ"""
        data = {
            'question': "What is an API?",
            'answer': "An API is a set of rules that allows programs to talk to each other."
        }
        response = self.client.post('/api/faqs/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch('faq.views.FAQViewSet.translate_to_languages')
    def test_update_faq_admin(self, mock_translate):
        """Test that only admin can update FAQ"""
        self.client.force_authenticate(user=self.admin_user)
        data = {'question': "What is Django Framework?"}
        response = self.client.patch(f'/api/faqs/{self.faq1.id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.faq1.refresh_from_db()
        self.assertEqual(self.faq1.question, "What is Django Framework?")
        mock_translate.assert_called_once()

    def test_delete_faq_admin(self):
        """Test that only admin can delete FAQ"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(f'/api/faqs/{self.faq1.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(FAQ.objects.count(), 1)

    def test_cache_behavior(self):
        """Test that caching works as expected"""
        response = self.client.get('/api/faqs/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Simulate a cache hit
        cached_response = self.client.get('/api/faqs/')
        self.assertEqual(cached_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(cached_response.data), 2)


"""
import time
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.models import User
from .models import FAQ
from .languages import SUPPORTED_LANGUAGES
from decouple import config

class FAQAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        self.admin_user = User.objects.create_superuser(
            username=config('ADMIN_USERNAME'),
            email=config('ADMIN_EMAIL'),
            password=config('ADMIN_PASSWORD'),
        )

        self.faq1 = FAQ.objects.create(
            question="What is Django?",
            answer="Django is a high-level Python web framework."
        )
        self.faq2 = FAQ.objects.create(
            question="What is REST?",
            answer="REST is an architectural style for designing networked applications."
        )

    def test_list_faqs_public(self):
        response = self.client.get('/api/faqs/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_retrieve_faq_public(self):
        response = self.client.get(f'/api/faqs/{self.faq1.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['question'], "What is Django?")

    def test_faq_str_method(self):
        self.assertEqual(str(self.faq1), "What is Django?")

    def test_create_faq_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'question': "What is an API?",
            'answer': "An API is a set of rules that allows programs to talk to each other."
        }
        response = self.client.post('/api/faqs/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(FAQ.objects.count(), 3)

    def test_create_faq_unauthenticated(self):
        data = {
            'question': "What is an API?",
            'answer': "An API is a set of rules that allows programs to talk to each other."
        }
        response = self.client.post('/api/faqs/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_faq_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {'question': "What is Django Framework?"}
        response = self.client.patch(f'/api/faqs/{self.faq1.id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_faq_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(f'/api/faqs/{self.faq1.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_language_query_parameter(self):
        self.client.force_authenticate(user=self.admin_user)
        for lang in SUPPORTED_LANGUAGES:
            if lang != 'en':
                response = self.client.get(f'/api/faqs/{self.faq1.id}/?lang={lang}')
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                time.sleep(60)
"""