# MyFAQProject Documentation

- Deployed URL: https://myfaqs.onrender.com
- Admin Username: Sonugupta
- Admin Password: 12345
---

## Features

- **CRUD APIs**: Full Create, Read, Update, and Delete functionalities for managing FAQs via RESTful APIs. The ReadOnly APIs are accessible to normal user, while the remaining APIs are protected for Admin User.
- **Multi-language Support**: The application automatic translation of FAQs into top-5 languages (Spanish, Hindi, French, German, Chinese Simplified) at the moment it is created, and the remaining languages would be translated dynamically on the user request.
- **Background Tasks (Messaging Queues)**: The top-5 language translation is off-loaded to the Redis Messaging Queue (RQ) worker. This keeps main thread unblocked and responsive.
- **Caching**: Redis is used as cache store, which make response faster and efficient.
- **Admin Interface**: The admin panel contains a WYSIWYG editor to format FAQs question-answers, along with searching, sorting, and pagination features.
- **Security**:
  - CSRF protection and secure cookies.
  - Rate limiting to prevent abuse.
- **Custom Logging**: Detailed logging setup to monitor application behavior and capture errors.

---

## Setup Instructions

### Prerequisites

- **Python 3.8+**
- **Redis Server**: Required for caching and background task management.
- **Git**: For version control.
- **Virtual Environment Tool**: Such as `venv` or `virtualenv`.

### Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/Sonugupta2001/myFAQs.git
   cd MyFAQProject
   ```

2. **Create a Virtual Environment**

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**

  ```bash
  pip install -r requirements.txt
  ```

  *Ensure `requirements.txt` includes all required packages such as:*
  - Django
  - djangorestframework
  - django-ckeditor
  - django-rq
  - django-decouple
  - googletrans
  - django-redis
  - whitenoise

### Configuration

1. **Environment Variables**

   Create a `.env` file in the project root directory and define the following variables:

   ```env
   SECRET_KEY=your_secret_key
   DEBUG=False
   REDIS_HOST=localhost
   REDIS_PORT=6379
   REDIS_PASSWORD=your_redis_password
   ADMIN_USERNAME=admin
   ADMIN_EMAIL=admin@example.com
   ADMIN_PASSWORD=securepassword
   ```

2. **Apply Migrations**

   ```bash
   python manage.py migrate
   ```

3. **Create Superuser**

   ```bash
   python manage.py createsuperuser
   ```

4. **Collect Static Files**

   ```bash
   python manage.py collectstatic
   ```

### Running the Application

1. **Start Redis Server**

   Run the Redis server:

   ```bash
   redis-server
   ```

2. **Start Django Development Server**

   ```bash
   python manage.py runserver
   ```

3. **Start Django RQ Worker**

   Open a new terminal window/tab, activate the virtual environment, navigate to the project directory, and run:

   ```bash
   python manage.py rqworker
   ```

   *This worker would processe background translation tasks.*

4. **Access the Application**

   - **Admin Interface**: [http://localhost:8000/admin/](http://localhost:8000/admin/)
   - **API Endpoints**: [http://localhost:8000/api/faqs/](http://localhost:8000/api/faqs/)

---

## API Request-Response Format

### Authentication

- **Admin Users**: Must authenticate to perform create, update, and delete operations using Token Authentication.
- **Authenticated Users**: Can read FAQs.
- **Unauthenticated Users**: Can read FAQs but cannot modify them.

### Endpoints

All API endpoints are prefixed with `/api/faqs/`.

#### 1. List FAQs

Retrieve a list of all FAQs.

- **URL**: `/api/faqs/`
- **Method**: `GET`
- **Query Parameters**:
  - `lang` (optional): Language code (`en`, `es`, `hi`, `fr`, `de`, `zh_cn`).
  - Defaults to `en`.

- **Request Example**:

  ```http
  GET /api/faqs/?lang=es HTTP/1.1
  Host: localhost:8000
  ```

- **Successful Response** (`200 OK`):

  ```json
  [
      {
          "id": 1,
          "question": "¿Qué es Django?",
          "answer": "Django es un framework web de alto nivel en Python.",
          "created_at": "2023-10-01T12:34:56Z"
      },
      {
          "id": 2,
          "question": "¿Qué es REST?",
          "answer": "REST es un estilo arquitectónico para diseñar aplicaciones en red.",
          "created_at": "2023-10-01T12:35:56Z"
      }
  ]
  ```

- **Cached Response**:

  If the response is cached, it will be returned immediately without triggering translation tasks.

- **Translation Pending**:

  If translations are pending, the response includes a header `translation_pending: true` to indicate that the translation is still pending (mainly due to rate limiting of google API).

  ```json
  [
      {
          "id": 1,
          "question": "What is Django?",
          "answer": "Django is a high-level Python web framework.",
          "created_at": "2023-10-01T12:34:56Z",
          "translation_pending": true
      },
      ...
  ]
  ```

#### 2. Retrieve FAQ

Retrieve details of a specific FAQ by its ID.

- **URL**: `/api/faqs/<id>/`
- **Method**: `GET`
- **Query Parameters**:
  - `lang` (optional): Language code (`en`, `es`, `hi`, `fr`, `de`, `zh_cn`). 
  - Defaults to `en`.

- **Request Example**:

  ```http
  GET /api/faqs/1/?lang=fr HTTP/1.1
  Host: localhost:8000
  ```

- **Successful Response** (`200 OK`):

  ```json
  {
      "id": 1,
      "question": "Qu'est-ce que Django?",
      "answer": "Django est un framework web Python de haut niveau.",
      "created_at": "2023-10-01T12:34:56Z"
  }
  ```

- **Translation Pending** (`202 Accepted`):

  If translation is not yet available, the response includes `translation_pending: true`.

  ```json
  {
      "id": 1,
      "question": "What is Django?",
      "answer": "Django is a high-level Python web framework.",
      "created_at": "2023-10-01T12:34:56Z",
      "translation_pending": true
  }
  ```

#### 3. [Admin Only] Create FAQ

Create a new FAQ entry.

- **URL**: `/api/faqs/`
- **Method**: `POST`
- **Headers**:
  - `Authorization: Token <admin_token>`

- **Request Body**:

  ```json
  {
      "question": "What is an API?",
      "answer": "An API is a set of rules that allows programs to talk to each other."
  }
  ```

- **Successful Response** (`201 Created`):

  ```json
  {
      "id": 3,
      "question": "What is an API?",
      "answer": "An API is a set of rules that allows programs to talk to each other.",
      "created_at": "2023-10-01T13:00:00Z",
      "updated_at": "2023-10-01T13:00:00Z"
  }
  ```

- **Translation Triggered**:

  After creation, background translation tasks are pushed into the message queue to translate the new FAQ into the top-5 supported languages.

#### 4.[Admin Only] Update FAQ

Update an existing FAQ.

- **URL**: `/api/faqs/<id>/`
- **Method**: `PATCH`
- **Headers**:
  - `Authorization: Token <admin_token>`

- **Request Body**:

  ```json
  {
      "question": "What is the Django Framework?"
  }
  ```

- **Successful Response** (`200 OK`):

  ```json
  {
      "id": 1,
      "question": "What is the Django Framework?",
      "answer": "Django is a high-level Python web framework.",
      "question_es": "¿Qué es el marco Django?",
      "answer_es": "Django es un framework web de alto nivel en Python.",
      "created_at": "2023-10-01T12:34:56Z",
      "updated_at": "2023-10-01T13:05:00Z"
  }
  ```

- **Translation Triggered**:

  After updating, background translation tasks are enqueued to update translations in all supported languages.

#### 5. [Admin Only] Delete FAQ

Delete an existing FAQ.

- **URL**: `/api/faqs/<id>/`
- **Method**: `DELETE`
- **Headers**:
  - `Authorization: Token <admin_token>`

- **Successful Response** (`204 No Content`):

---

### Error Responses

The API provides meaningful error messages and appropriate HTTP status codes for various failure scenarios.

#### Common Error Responses

| Status Code             | Description                                                                                   | Example Response                                           |
|-------------------------|-----------------------------------------------------------------------------------------------|------------------------------------------------------------|
| `400 Bad Request`       | Invalid input data.                                                                           | `{"detail": "Invalid data."}`                              |
| `401 Unauthorized`      | Authentication credentials were not provided or are invalid.                                  | `{"detail": "Authentication credentials were not provided."}` |
| `403 Forbidden`         | User does not have permission to perform the action.                                         | `{"detail": "You do not have permission to perform this action."}` |
| `404 Not Found`         | The requested resource does not exist.                                                       | `{"detail": "Not found."}`                                 |
| `405 Method Not Allowed`| HTTP method not supported for the endpoint.                                                  | `{"detail": "Method \"PUT\" not allowed."}`                |
| `500 Internal Server Error`| An unexpected error occurred on the server.                                                  | `{"detail": "Internal server error."}`                     |

---

## Note:
- Since I've used the Google Translate API for translating the FAQs, the google API has a rigid rate limiting and throttling mechanism. So some API requests, specifically those which involves accessing the FAQs in a less-common language (which are not supported by our top-5 popular language list), may face a significant delay. Although I've implemented sleep/delays between consecutive google API requests, but still it may face rate limiting. In that case, we have no other option except to retry again, after the specified amount of time-period, which I've implemented in those API endpoints.
- The main concern is, some API endpoints and tests may consume a significant time or get failed as well. And here I've explained why it might happen.

## License

This project is licensed under the [MIT License](LICENSE).

---
