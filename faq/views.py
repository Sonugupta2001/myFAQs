from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAdminUser
from django.core.cache import cache
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django_rq import enqueue
from .models import FAQ
from .serializers import FAQSerializer
from .languages import SUPPORTED_LANGUAGES
from .tasks import translate_faq

class FAQViewSet(viewsets.ModelViewSet):
    queryset = FAQ.objects.all()
    serializer_class = FAQSerializer

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
        translated_faqs = []

        for faq in queryset:
            if lang == 'en':
                translated_faqs.append({
                    'id': faq.id,
                    'question': faq.question,
                    'answer': faq.answer,
                    'created_at': faq.created_at,
                })
            else:
                question_field = f'question_{lang}'
                answer_field = f'answer_{lang}'
                question = getattr(faq, question_field, None)
                answer = getattr(faq, answer_field, None)

                if question and answer:
                    translated_faqs.append({
                        'id': faq.id,
                        'question': question,
                        'answer': answer,
                        'created_at': faq.created_at,
                    })
                else:
                    enqueue(translate_faq, faq.id)
                    translated_faqs.append({
                        'id': faq.id,
                        'question': faq.question,
                        'answer': faq.answer,
                        'created_at': faq.created_at,
                        'translation_pending': True,
                    })

        cache.set(cache_key, translated_faqs, timeout=60*10)
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

        if lang == 'en':
            serializer = self.get_serializer(instance)
            return Response(serializer.data)

        question_field = f'question_{lang}'
        answer_field = f'answer_{lang}'
        question = getattr(instance, question_field, None)
        answer = getattr(instance, answer_field, None)

        if question and answer:
            translated_faq = {
                'id': instance.id,
                'question': question,
                'answer': answer,
                'created_at': instance.created_at,
            }
            cache.set(cache_key, translated_faq, timeout=60*10)
            return Response(translated_faq)
        else:
            enqueue(translate_faq, instance.id)
            translated_faq = {
                'id': instance.id,
                'question': instance.question,
                'answer': instance.answer,
                'created_at': instance.created_at,
                'translation_pending': True,
            }
            return Response(translated_faq, status=status.HTTP_202_ACCEPTED)

    @method_decorator(staff_member_required)
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        faq_id = response.data['id']
        enqueue(translate_faq, faq_id)
        return response

    @method_decorator(staff_member_required)
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        self.invalidate_faq_cache(instance)
        response = super().update(request, *args, **kwargs)
        enqueue(translate_faq, instance.id)
        return response

    @method_decorator(staff_member_required)
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        self.invalidate_faq_cache(instance)
        response = super().partial_update(request, *args, **kwargs)
        enqueue(translate_faq, instance.id)
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
