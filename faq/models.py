from django.db import models
from ckeditor.fields import RichTextField
from django.contrib.auth.models import User
from googletrans import Translator
from asgiref.sync import sync_to_async
import asyncio

class FAQ(models.Model):
    question = models.TextField()
    answer = RichTextField()
    created_at = models.DateTimeField(auto_now_add=True)
    question_hi = models.TextField(blank=True, null=True)
    answer_hi = RichTextField(blank=True, null=True)
    question_es = models.TextField(blank=True, null=True)
    answer_es = RichTextField(blank=True, null=True)
    question_fr = models.TextField(blank=True, null=True)
    answer_fr = RichTextField(blank=True, null=True)
    question_de = models.TextField(blank=True, null=True)
    answer_de = RichTextField(blank=True, null=True)
    question_zh = models.TextField(blank=True, null=True)
    answer_zh = RichTextField(blank=True, null=True)

    def __str__(self):
        return self.question