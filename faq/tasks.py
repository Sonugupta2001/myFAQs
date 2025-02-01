from django_rq import job
from django.core.cache import cache
from django.db import transaction
from googletrans import Translator
from .models import FAQ
from .languages import SUPPORTED_LANGUAGES

@job
def translate_faq(faq_id):
    try:
        faq = FAQ.objects.get(id=faq_id)
    except FAQ.DoesNotExist:
        return

    translator = Translator()

    for lang in SUPPORTED_LANGUAGES:
        if lang == 'en':
            continue

        question_field = f'question_{lang}'
        answer_field = f'answer_{lang}'
        question = getattr(faq, question_field, None)
        answer = getattr(faq, answer_field, None)

        if not question or not answer:
            try:
                translated_question = translator.translate(faq.question, dest=lang).text
                translated_answer = translator.translate(faq.answer, dest=lang).text

                setattr(faq, question_field, translated_question)
                setattr(faq, answer_field, translated_answer)

                with transaction.atomic():
                    faq.save()

                cache_key = f'faq_{faq.id}_{lang}'
                translated_faq = {
                    'id': faq.id,
                    'question': translated_question,
                    'answer': translated_answer,
                    'created_at': faq.created_at,
                }
                cache.set(cache_key, translated_faq, timeout=60*10)

            except Exception as e:
                print(f"Error translating FAQ {faq.id} to {lang}: {e}")

    for lang in SUPPORTED_LANGUAGES:
        if lang == 'en':
            continue
        cache_key = f'faqs_{lang}'
        faqs = FAQ.objects.all()
        translated_faqs = []
        for faq in faqs:
            q_field = f'question_{lang}'
            a_field = f'answer_{lang}'
            question = getattr(faq, q_field, None)
            answer = getattr(faq, a_field, None)
            if question and answer:
                translated_faqs.append({
                    'id': faq.id,
                    'question': question,
                    'answer': answer,
                    'created_at': faq.created_at,
                })
        cache.set(cache_key, translated_faqs, timeout=60*10)