import time
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.core.cache import cache
from .models import FAQ
from .languages import SUPPORTED_LANGUAGES

class FAQAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.faq1 = FAQ.objects.create(
            question="What is Django?",
            answer="Django is a high-level Python web framework."
        )
        self.faq2 = FAQ.objects.create(
            question="What is REST?",
            answer="REST is an architectural style for designing networked applications."
        )

    def dynamic_sleep(self, response):
        if response.status_code == 429:
            retry_after = response.headers.get('Retry-After')
            if retry_after:
                time.sleep(int(retry_after))

    def test_list_faqs(self):
        response = self.client.get('/api/faqs/')
        if response.status_code == 429:
            self.dynamic_sleep(response)
            response = self.client.get('/api/faqs/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_retrieve_faq(self):
        response = self.client.get(f'/api/faqs/{self.faq1.id}/')
        if response.status_code == 429:
            self.dynamic_sleep(response)
            response = self.client.get(f'/api/faqs/{self.faq1.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['question'], "What is Django?")

    def test_language_query_parameter(self):
        for lang in SUPPORTED_LANGUAGES:
            if lang != 'en':
                response = self.client.get(f'/api/faqs/{self.faq1.id}/?lang={lang}')
                if response.status_code == 429:
                    self.dynamic_sleep(response)
                    response = self.client.get(f'/api/faqs/{self.faq1.id}/?lang={lang}')
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertNotEqual(response.data['question'], "What is Django?")

    def test_create_faq(self):
        data = {
            'question': "What is an API?",
            'answer': "An API is a set of rules that allows programs to talk to each other."
        }
        response = self.client.post('/api/faqs/', data, format='json')
        if response.status_code == 429:
            self.dynamic_sleep(response)
            response = self.client.post('/api/faqs/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(FAQ.objects.count(), 3)
        self.assertEqual(FAQ.objects.get(id=response.data['id']).question, "What is an API?")

    def test_update_faq(self):
        data = {'question': "What is Django Framework?"}
        response = self.client.patch(f'/api/faqs/{self.faq1.id}/', data, format='json')
        if response.status_code == 429:
            self.dynamic_sleep(response)
            response = self.client.patch(f'/api/faqs/{self.faq1.id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(FAQ.objects.get(id=self.faq1.id).question, "What is Django Framework?")

    def test_delete_faq(self):
        response = self.client.delete(f'/api/faqs/{self.faq1.id}/')
        if response.status_code == 429:
            self.dynamic_sleep(response)
            response = self.client.delete(f'/api/faqs/{self.faq1.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(FAQ.objects.count(), 1)

    def test_cache_behavior(self):
        lang = 'hi'
        cache_key = f'faq_{self.faq1.id}_{lang}'
        cache.clear()
        response = self.client.get(f'/api/faqs/{self.faq1.id}/?lang={lang}')
        if response.status_code == 429:
            self.dynamic_sleep(response)
            response = self.client.get(f'/api/faqs/{self.faq1.id}/?lang={lang}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(cache.get(cache_key))

    def test_unsupported_language_fallback(self):
        response = self.client.get(f'/api/faqs/{self.faq1.id}/?lang=unsupported')
        if response.status_code == 429:
            self.dynamic_sleep(response)
            response = self.client.get(f'/api/faqs/{self.faq1.id}/?lang=unsupported')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['question'], "What is Django?")