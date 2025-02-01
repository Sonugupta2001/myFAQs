from django.contrib import admin
from .models import FAQ

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    exclude = [
        'question_hi', 'answer_hi',
        'question_es', 'answer_es',
        'question_fr', 'answer_fr',
        'question_de', 'answer_de',
        'question_zh', 'answer_zh'
    ]
    
    list_display = ['question', 'answer','created_at']

    search_fields = ['question', 'answer']

    ordering = ['created_at']

    list_filter = ['created_at']

    list_per_page = 10