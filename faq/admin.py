from django.contrib import admin
from .models import FAQ

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ['question', 'answer','created_at']

    search_fields = ['question', 'answer']

    ordering = ['created_at']

    list_filter = ['created_at']

    # pagination (10 entries per page)
    list_per_page = 10