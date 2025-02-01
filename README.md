# FAQ Management System

## Overview

The FAQ Management System allows users to manage frequently asked questions with support for multiple languages. It includes a rich text editor for formatting answers and uses Redis for caching to enhance performance. The application is built using Django and Django REST Framework.


## Installation and Setup

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/Sonugupta2001/myFAQs.git
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

- **Run Tests**: Used Django's testing framework to run unit tests for testing API responses and models.
Since some tests use google translate APIs and google API implements rate limiting which was causing the http error "429 Too Many Requests". So, I implemented the sleep mechanism which utilises the "retry_after" header provided in the repsonse of google translate API when it fails, to retry the test after the provided time.

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

- **FAQ Model**: Model of the FAQs includes fields for the question and answer. By default, the FAQs through admin pannel are created in english and when the client requests the FAQs in a particular language they are translated dynamically in the backend through google translate API.

### Views and URLs

- **Viewsets**: The application uses Django REST Framework's viewsets to handle CRUD operations for FAQs. The viewsets automatically map HTTP methods to actions like `list`, `create`, `retrieve`, `update`, and `destroy`.


- **URLs**: The application uses routers to generate URL patterns for the viewsets, simplifying the process of defining API endpoints.


### Serializers

- **FAQ Serializer**: Defined in `serializers.py`, this component converts FAQ model instances to JSON format and vice versa, ensuring data is correctly structured for API responses.

### WYSIWYG Editor

- **Integration**: The application integrates `django-ckeditor` to provide a rich text editor for formatting FAQ answers. This allows administrators to create visually appealing content without writing HTML.


### Admin Interface

- **Django Admin**: The FAQ model is registered in the admin interface, allowing administrators to manage FAQs easily. It implements pagination, searching and sorting mechanism for efficient FAQs management.
The admin interface is customized to include the WYSIWYG editor for rich text formatting.

### Caching

- **Redis Caching**: The application is configured to use Redis (cloud instance) as the caching backend, improving performance by storing translations and frequently accessed data.


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

- **Automated Translations**: The application uses `googletrans` to automatically translate FAQ questions into multiple languages when a user requests the FAQs in a partciular language. It provides a fallback to English if translations are unavailable.
Application supoorts over 100+ languages for translation.


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---
