from django.contrib import admin
from django.urls import include, path
from django.http import HttpResponse
from django.conf import settings
from django.urls import path, include


urlpatterns = [
    path('', lambda request: HttpResponse('Welcome to MyFAQProject!'), name='home'),
    path('admin/', admin.site.urls),
    path('api/', include('faq.urls')),
    path('django-rq/', include('django_rq.urls')),
]