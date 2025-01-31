# FAQ Management System

## Overview

The FAQ Management System allows users to manage frequently asked questions with support for multiple languages. It includes a rich text editor for formatting answers and uses Redis for caching to enhance performance. The application is built using Django and Django REST Framework.


## Installation and Setup

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/yourusername/faq-management-system.git
   cd faq-management-system
   ```

2. **Create and Activate a Virtual Environment**:

   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. **Set Up Environment Variables**:

   Create a `.env` file in the project root with the following variables:

   ```plaintext
   REDIS_HOST=your_redis_host
   REDIS_PORT=your_redis_port
   REDIS_PASSWORD=your_redis_password
   ```

4. **Apply Migrations**:

   ```bash
   python manage.py migrate
   ```

5. **Run the Development Server**:

   ```bash
   python manage.py runserver
   ```

6. **Build and Run the Docker Container**:

   ```bash
   docker-compose up --build
   ```


   The application will be available at `http://localhost:8000`.


## Testing

- **Run Tests**: Use Django's testing framework to run unit tests and ensure the application functions as expected.

  ```bash
  python manage.py test
  ```

## API Endpoints

The application provides the following API endpoints for managing FAQs:

- **List FAQs**: `GET /api/faqs/`
- **Retrieve FAQ**: `GET /api/faqs/<id>/`
- **Create FAQ**: `POST /api/faqs/`
- **Update FAQ**: `PATCH /api/faqs/<id>/`
- **Delete FAQ**: `DELETE /api/faqs/<id>/`


## Components

### Models

- **FAQ Model**: The core data structure of the application, defined in `models.py`. It includes fields for the question, answer, and translations in multiple languages. The model also includes a method to retrieve translated text dynamically.

  ```python
  class FAQ(models.Model):
      question = models.TextField()
      answer = RichTextField()
      question_hi = models.TextField(blank=True, null=True)
      question_bn = models.TextField(blank=True, null=True)

      def get_translated_question(self, lang='en'):
          if lang == 'hi' and self.question_hi:
              return self.question_hi
          elif lang == 'bn' and self.question_bn:
              return self.question_bn
          return self.question
  ```

### Views and URLs

- **Viewsets**: The application uses Django REST Framework's viewsets to handle CRUD operations for FAQs. The viewsets automatically map HTTP methods to actions like `list`, `create`, `retrieve`, `update`, and `destroy`.

  ```python
  class FAQViewSet(viewsets.ModelViewSet):
      queryset = FAQ.objects.all()
      serializer_class = FAQSerializer
  ```

- **URLs**: The application uses routers to generate URL patterns for the viewsets, simplifying the process of defining API endpoints.

  ```python
  router = DefaultRouter()
  router.register(r'faqs', FAQViewSet)
  ```

### Serializers

- **FAQ Serializer**: Defined in `serializers.py`, this component converts FAQ model instances to JSON format and vice versa, ensuring data is correctly structured for API responses.

  ```python
  class FAQSerializer(serializers.ModelSerializer):
      class Meta:
          model = FAQ
          fields = '__all__'
  ```

### Admin Interface

- **Django Admin**: The FAQ model is registered in the admin interface, allowing administrators to manage FAQs easily. The admin interface is customized to include the WYSIWYG editor for rich text formatting.

  ```python
  @admin.register(FAQ)
  class FAQAdmin(admin.ModelAdmin):
      list_display = ['question', 'answer']
  ```

### WYSIWYG Editor

- **Integration**: The application integrates `django-ckeditor` to provide a rich text editor for formatting FAQ answers. This allows administrators to create visually appealing content without writing HTML.

### Caching

- **Redis Caching**: The application is configured to use Redis as the caching backend, improving performance by storing translations and frequently accessed data.

  ```python
  CACHES = {
      'default': {
          'BACKEND': 'django_redis.cache.RedisCache',
          'LOCATION': 'redis://<host>:<port>/0',
          'OPTIONS': {
              'CLIENT_CLASS': 'django_redis.client.DefaultClient',
              'PASSWORD': '<password>',
          }
      }
  }
  ```

### Translation

- **Automated Translations**: The application uses `googletrans` to automatically translate FAQ questions into multiple languages during creation. It provides a fallback to English if translations are unavailable.

  ```python
  def save(self, *args, **kwargs):
      translator = Translator()
      if not self.question_hi:
          self.question_hi = translator.translate(self.question, dest='hi').text
      if not self.question_bn:
          self.question_bn = translator.translate(self.question, dest='bn').text
      super().save(*args, **kwargs)
  ```



## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---