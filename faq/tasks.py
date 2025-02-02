from django_rq import job
from django.core.cache import cache
from django.db import transaction
from googletrans import Translator
from .models import FAQ
from .languages import SUPPORTED_LANGUAGES
from django.utils.html import strip_tags
import logging
import time
import random

logger = logging.getLogger(__name__)

@job
def translate_faq(faq_id):
    try:
        faq = FAQ.objects.get(id=faq_id)
    except FAQ.DoesNotExist:
        logger.error(f"FAQ with id {faq_id} does not exist.")
        return

    translator = Translator()

    for lang in SUPPORTED_LANGUAGES:
        if lang == 'en':
            continue

        question_field = f'question_{lang}'
        answer_field = f'answer_{lang}'

        question_translation = getattr(faq, question_field, None)
        answer_translation = getattr(faq, answer_field, None)

        needs_save = False

        delay_seconds = 10
        max_retries = 3
        retry_delay = 60*10

        if not question_translation:
            for attempt in range(max_retries):
                try:
                    time.sleep(delay_seconds)
                    translated_question = translator.translate(faq.question, dest=lang).text
                    setattr(faq, question_field, translated_question)
                    needs_save = True
                    break
                except Exception as e:
                    logger.error(f"Error translating FAQ {faq.id} question to {lang}: {e}", exc_info=True)
                    if '429' in str(e):
                        wait_time = retry_delay * (2 ** attempt)
                        logger.info(f"Rate limited. Waiting {wait_time} seconds before retrying.")
                        time.sleep(wait_time)
                    else:
                        break

        if not answer_translation:
            for attempt in range(max_retries):
                try:
                    time.sleep(delay_seconds)
                    original_answer_text = strip_tags(faq.answer)
                    translated_answer = translator.translate(original_answer_text, dest=lang).text
                    setattr(faq, answer_field, translated_answer)
                    needs_save = True
                    break
                except Exception as e:
                    logger.error(f"Error translating FAQ {faq.id} answer to {lang}: {e}", exc_info=True)
                    if '429' in str(e):
                        wait_time = retry_delay * (2 ** attempt)
                        logger.info(f"Rate limited. Waiting {wait_time} seconds before retrying.")
                        time.sleep(wait_time)
                    else:
                        break

        if needs_save:
            with transaction.atomic():
                faq.save()

        cache_key = f'faq_{faq.id}_{lang}'
        translated_faq = {
            'id': faq.id,
            'question': getattr(faq, question_field, faq.question),
            'answer': getattr(faq, answer_field, faq.answer),
            'created_at': faq.created_at,
        }
        cache.set(cache_key, translated_faq, timeout=60*10)

    for lang in SUPPORTED_LANGUAGES:
        if lang == 'en':
            continue

        cache_key = f'faqs_{lang}'
        faqs = FAQ.objects.all()
        translated_faqs = []

        for faq_instance in faqs:
            q_field = f'question_{lang}'
            a_field = f'answer_{lang}'
            question = getattr(faq_instance, q_field, None)
            answer = getattr(faq_instance, a_field, None)

            if question and answer:
                translated_faqs.append({
                    'id': faq_instance.id,
                    'question': question,
                    'answer': answer,
                    'created_at': faq_instance.created_at,
                })
            else:
                translated_faqs.append({
                    'id': faq_instance.id,
                    'question': faq_instance.question,
                    'answer': faq_instance.answer,
                    'created_at': faq_instance.created_at,
                    'translation_pending': True,
                })

        cache.set(cache_key, translated_faqs, timeout=60*10)