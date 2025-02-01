# FAQ Management System

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




## API Endpoints

### Public APIs
#### 1. List FAQs
- **Endpoint**: `GET /api/faqs/`
- **Description**: Retrieves a list of all FAQs.
- **Query Parameters**: 
  - `lang` (optional): Language code for translated content (e.g., 'hi', 'bn').
- **Sample Request**:
  ```http
  GET /api/faqs/?lang=hi
  ```
- **Sample Response**:
  ```json
  [
      {
          "id": 1,
          "question": "Django क्या है?",
          "answer": "Django एक उच्च-स्तरीय Python वेब फ्रेमवर्क है।",
          "created_at": "2024-01-20T10:30:00Z"
      },
      {
          "id": 2,
          "question": "REST क्या है?",
          "answer": "REST नेटवर्क अनुप्रयोगों को डिज़ाइन करने के लिए एक वास्तुशिल्प शैली है।",
          "created_at": "2024-01-20T10:35:00Z"
      }
  ]
  ```

#### 2. Retrieve FAQ
- **Endpoint**: `GET /api/faqs/<id>/`
- **Description**: Retrieves a specific FAQ by ID.
- **Query Parameters**: 
  - `lang` (optional): Language code for translated content.
- **Sample Request**:
  ```http
  GET /api/faqs/1/?lang=hi
  ```
- **Sample Response**:
  ```json
  {
      "id": 1,
      "question": "Django क्या है?",
      "answer": "Django एक उच्च-स्तरीय Python वेब फ्रेमवर्क है।",
      "created_at": "2024-01-20T10:30:00Z"
  }
  ```


### Restricted(Admin-Only) APIs

#### 1. Create FAQ
- **Endpoint**: `POST /api/faqs/`
- **Description**: Creates a new FAQ. (Admin only)
- **Request Body**:
  ```json
  {
      "question": "What is an API?",
      "answer": "An API is a set of rules that allows programs to talk to each other."
  }
  ```
- **Sample Response**:
  ```json
  {
      "id": 3,
      "question": "What is an API?",
      "answer": "An API is a set of rules that allows programs to talk to each other.",
      "created_at": "2024-01-20T11:00:00Z"
  }
  ```

#### 2. Update FAQ
- **Endpoint**: `PATCH /api/faqs/<id>/`
- **Description**: Updates an existing FAQ. (Admin only)
- **Request Body**:
  ```json
  {
      "question": "What is Django Framework?",
      "answer": "Django is a high-level Python web framework that enables rapid development of secure and maintainable websites."
  }
  ```
- **Sample Response**:
  ```json
  {
      "id": 1,
      "question": "What is Django Framework?",
      "answer": "Django is a high-level Python web framework that enables rapid development of secure and maintainable websites.",
      "created_at": "2024-01-20T10:30:00Z"
  }
  ```

#### 3. Delete FAQ
- **Endpoint**: `DELETE /api/faqs/<id>/`
- **Description**: Deletes a specific FAQ. (Admin only)
- **Response**: Returns HTTP 204 No Content on successful deletion.


## Error Responses

1. **Not Found (404)**:
   - **Description**: The requested resource does not exist.
   - **Response**:
     ```json
     {
         "detail": "Not found."
     }
     ```

2. **Unauthorized (401)**:
   - **Description**: Authentication credentials were not provided or are invalid.
   - **Response**:
     ```json
     {
         "detail": "Authentication credentials were not provided."
     }
     ```

3. **Forbidden (403)**:
   - **Description**: The user does not have permission to perform the action (e.g., non-admin trying to create an FAQ).
   - **Response**:
     ```json
     {
         "detail": "You do not have permission to perform this action."
     }
     ```

4. **Rate Limit Exceeded (429)**:
   - **Description**: Too many requests have been made in a short period.
   - **Response**:
     ```json
     {
         "detail": "Request was throttled. Expected available in <X> seconds."
     }
     ```

5. **Bad Request (400)**:
   - **Description**: The request was malformed or invalid.
   - **Response**:
     ```json
     {
         "error": "Invalid request parameters"
     }
     ```



## Testing

- **Run Tests**: Used Django's testing framework to run unit tests for testing API responses and models.
Since some tests use google translate APIs and google API implements rate limiting which was causing the http error "429 Too Many Requests". So, I implemented the sleep mechanism which utilises the "retry_after" header provided in the repsonse of google translate API when it fails, to retry the test after the provided time.

  ```bash
  python manage.py test
  ```



## Components

### Models

- **FAQ Model**: Model of the FAQs includes fields for the question and answer. By default, the FAQs through admin pannel are created in english and when the client requests the FAQs in a particular language they are translated dynamically in the backend through google translate API.

### Views and URLs

- **Viewsets**: The application uses Django REST Framework's viewsets to handle CRUD operations for FAQs.


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