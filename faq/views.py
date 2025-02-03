from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAdminUser
from django.core.cache import cache
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django_rq import get_queue
from .models import FAQ
from .serializers import FAQSerializer
from .languages import SUPPORTED_LANGUAGES
from .tasks import translate_faq
import logging
from rq import Retry

logger = logging.getLogger(__name__)

CACHE_TIMEOUT = 60 * 10

class FAQViewSet(viewsets.ModelViewSet):
    queryset = FAQ.objects.all()
    serializer_class = FAQSerializer
    queue = get_queue()

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticatedOrReadOnly]
        return [permission() for permission in permission_classes]

    def get_translated_faq(self, faq, lang):
        if lang == 'en':
            return {
                'id': faq.id,
                'question': faq.question,
                'answer': faq.answer,
                'created_at': faq.created_at,
            }
        else:
            question_field = f'question_{lang}'
            answer_field = f'answer_{lang}'
            question = getattr(faq, question_field, None)
            answer = getattr(faq, answer_field, None)

            if question and answer:
                return {
                    'id': faq.id,
                    'question': question,
                    'answer': answer,
                    'created_at': faq.created_at,
                }
            else:
                self.queue.enqueue(translate_faq, faq.id, retry=Retry(max=3, interval=[60]))

                return {
                    'id': faq.id,
                    'question': faq.question,
                    'answer': faq.answer,
                    'created_at': faq.created_at,
                    'translation_pending': True,
                }

    def list(self, request, *args, **kwargs):
        lang = request.query_params.get('lang', 'en')
        if lang not in SUPPORTED_LANGUAGES:
            lang = 'en'

        cache_key = f'faqs_{lang}'
        cached_faqs = cache.get(cache_key)

        if cached_faqs is not None:
            return Response(cached_faqs)

        queryset = self.get_queryset()
        translated_faqs = []

        for faq in queryset:
            translated_faq = self.get_translated_faq(faq, lang)
            translated_faqs.append(translated_faq)

        cache.set(cache_key, translated_faqs, timeout=CACHE_TIMEOUT)
        return Response(translated_faqs)

    def retrieve(self, request, *args, **kwargs):
        lang = request.query_params.get('lang', 'en')
        if lang not in SUPPORTED_LANGUAGES:
            lang = 'en'

        instance = self.get_object()
        cache_key = f'faq_{instance.id}_{lang}'
        cached_faq = cache.get(cache_key)

        if cached_faq is not None:
            return Response(cached_faq)

        response_data = self.get_translated_faq(instance, lang)
        cache.set(cache_key, response_data, timeout=CACHE_TIMEOUT)
        return Response(response_data)

    @method_decorator(staff_member_required)
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        faq_id = response.data['id']

        self.queue.enqueue(translate_faq, faq.id, retry=Retry(max=3, interval=[60]))
        return response

    @method_decorator(staff_member_required)
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        self.invalidate_faq_cache(instance)
        response = super().update(request, *args, **kwargs)

        self.queue.enqueue(translate_faq, faq.id, retry=Retry(max=3, interval=[60]))
        return response

    @method_decorator(staff_member_required)
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        self.invalidate_faq_cache(instance)
        response = super().partial_update(request, *args, **kwargs)
        
        self.queue.enqueue(translate_faq, faq.id, retry=Retry(max=3, interval=[60]))
        return response

    @method_decorator(staff_member_required)
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.invalidate_faq_cache(instance)
        response = super().destroy(request, *args, **kwargs)
        return response

    def invalidate_faq_cache(self, instance):
        for lang in SUPPORTED_LANGUAGES:
            cache.delete(f'faqs_{lang}')
            cache.delete(f'faq_{instance.id}_{lang}')