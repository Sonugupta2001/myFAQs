from rest_framework import viewsets
from rest_framework.response import Response
from googletrans import Translator
from django.core.cache import cache
from .models import FAQ
from .serializers import FAQSerializer
from .languages import SUPPORTED_LANGUAGES

class FAQViewSet(viewsets.ModelViewSet):
    queryset = FAQ.objects.all()
    serializer_class = FAQSerializer


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
                translated_faq = {
                    'id': faq.id,
                    'question': translator.translate(faq.question, dest=lang).text,
                    'answer': translator.translate(faq.answer, dest=lang).text,
                    'created_at': faq.created_at,
                }
                translated_faqs.append(translated_faq)
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
            translated_faq = {
                'id': instance.id,
                'question': translator.translate(instance.question, dest=lang).text,
                'answer': translator.translate(instance.answer, dest=lang).text,
                'created_at': instance.created_at,
            }
            cache.set(cache_key, translated_faq, timeout=60*10)
            return Response(translated_faq)

        serializer = self.get_serializer(instance)
        return Response(serializer.data)