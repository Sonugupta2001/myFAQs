from django.core.cache import cache
from rest_framework import viewsets
from .models import FAQ
from .serializers import FAQSerializer

class FAQViewSet(viewsets.ModelViewSet):
    queryset = FAQ.objects.all()
    serializer_class = FAQSerializer

    def get_queryset(self):
        lang = self.request.query_params.get('lang', 'en')
        cache_key = f'faqs_{lang}'
        cached_faqs = cache.get(cache_key)

        if cached_faqs is not None:
            return cached_faqs

        queryset = super().get_queryset()
        for faq in queryset:
            faq.question = faq.get_translated_question(lang)

        cache.set(cache_key, queryset, timeout=60*15)
        return queryset