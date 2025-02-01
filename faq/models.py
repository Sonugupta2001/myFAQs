from django.db import models
from ckeditor.fields import RichTextField
from django.contrib.auth.models import User

class FAQ(models.Model):
    question = models.TextField()
    answer = RichTextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question