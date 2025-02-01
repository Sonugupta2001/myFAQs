from django.db import models

class FAQ(models.Model):
    question = models.TextField()
    answer = models.TextField()
    question_es = models.TextField(blank=True, null=True)
    answer_es = models.TextField(blank=True, null=True)
    question_hi = models.TextField(blank=True, null=True)
    answer_hi = models.TextField(blank=True, null=True)
    question_fr = models.TextField(blank=True, null=True)
    answer_fr = models.TextField(blank=True, null=True)
    question_de = models.TextField(blank=True, null=True)
    answer_de = models.TextField(blank=True, null=True)
    question_zh_cn = models.TextField(blank=True, null=True)
    answer_zh_cn = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)