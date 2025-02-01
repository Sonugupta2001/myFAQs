import time
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAdminUser
from googletrans import Translator
from django.core.cache import cache
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from .models import FAQ
from .serializers import FAQSerializer
from .languages import SUPPORTED_LANGUAGES

class FAQViewSet(viewsets.ModelViewSet):
    queryset = FAQ.objects.all()
    serializer_class = FAQSerializer
    request_count = 0  # Track the number of requests

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticatedOrReadOnly]
        return [permission() for permission in permission_classes]

    def list(self, request, *args, **kwargs):
        lang = request.query_params.get('lang', 'en')
        if lang not in SUPPORTED_LANGUAGES:
            lang = 'en'

        cache_key = f'faqs_{lang}'
        cached_faqs = cache.get(cache_key)

        if cached_faqs is not None:
            return Response(cached_faqs)

        queryset = self.get_queryset()
        if lang != 'en':
            translator = Translator()
            translated_faqs = []
            for faq in queryset:
                if self.request_count >= 100:
                    time.sleep(60)
                    self.request_count = 0

                try:
                    translated_faq = {
                        'id': faq.id,
                        'question': translator.translate(faq.question, dest=lang).text,
                        'answer': translator.translate(faq.answer, dest=lang).text,
                        'created_at': faq.created_at,
                    }
                    translated_faqs.append(translated_faq)
                    self.request_count += 2
                except Exception as e:
                    if hasattr(e, 'response') and e.response.status_code == 429:
                        retry_after = int(e.response.headers.get('Retry-After', 60))
                        time.sleep(retry_after)
                        continue

            cache.set(cache_key, translated_faqs, timeout=60*10)
            return Response(translated_faqs)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        lang = request.query_params.get('lang', 'en')
        if lang not in SUPPORTED_LANGUAGES:
            lang = 'en'

        instance = self.get_object()
        cache_key = f'faq_{instance.id}_{lang}'
        cached_faq = cache.get(cache_key)

        if cached_faq is not None:
            return Response(cached_faq)

        if lang != 'en':
            translator = Translator()
            try:
                translated_faq = {
                    'id': instance.id,
                    'question': translator.translate(instance.question, dest=lang).text,
                    'answer': translator.translate(instance.answer, dest=lang).text,
                    'created_at': instance.created_at,
                }
                cache.set(cache_key, translated_faq, timeout=60*10)
                return Response(translated_faq)
            except Exception as e:
                if hasattr(e, 'response') and e.response.status_code == 429:
                    retry_after = int(e.response.headers.get('Retry-After', 60))
                    time.sleep(retry_after)
                    return self.retrieve(request, *args, **kwargs)

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @method_decorator(staff_member_required)
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @method_decorator(staff_member_required)
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        for lang in SUPPORTED_LANGUAGES:
            cache.delete(f'faqs_{lang}')
            cache.delete(f'faq_{instance.id}_{lang}')
        return super().update(request, *args, **kwargs)

    @method_decorator(staff_member_required)
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        for lang in SUPPORTED_LANGUAGES:
            cache.delete(f'faqs_{lang}')
            cache.delete(f'faq_{instance.id}_{lang}')
        return super().partial_update(request, *args, **kwargs)

    @method_decorator(staff_member_required)
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        for lang in SUPPORTED_LANGUAGES:
            cache.delete(f'faqs_{lang}')
            cache.delete(f'faq_{instance.id}_{lang}')
        return super().destroy(request, *args, **kwargs)