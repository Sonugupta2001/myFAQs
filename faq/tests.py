from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from .models import FAQ

class FAQAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.faq1 = FAQ.objects.create(
            question="What is Django?",
            answer="Django is a high-level Python web framework.",
            question_hi="Django क्या है?",
            question_bn="Django কি?",
        )
        self.faq2 = FAQ.objects.create(
            question="What is REST?",
            answer="REST is an architectural style for designing networked applications.",
        )

    def test_list_faqs(self):
        response = self.client.get('/api/faqs/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_retrieve_faq(self):
        response = self.client.get(f'/api/faqs/{self.faq1.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['question'], "What is Django?")

    def test_language_query_parameter(self):
        response = self.client.get(f'/api/faqs/{self.faq1.id}/?lang=hi')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['question'], "Django क्या है?")

    def test_create_faq(self):
        data = {
            'question': "What is an API?",
            'answer': "An API is a set of rules that allows programs to talk to each other.",
        }
        response = self.client.post('/api/faqs/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(FAQ.objects.count(), 3)
        self.assertEqual(FAQ.objects.get(id=response.data['id']).question, "What is an API?")

    def test_update_faq(self):
        data = {'question': "What is Django Framework?"}
        response = self.client.patch(f'/api/faqs/{self.faq1.id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(FAQ.objects.get(id=self.faq1.id).question, "What is Django Framework?")

    def test_delete_faq(self):
        response = self.client.delete(f'/api/faqs/{self.faq1.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(FAQ.objects.count(), 1)