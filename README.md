# MyFAQProject Documentation

- Deployed URL: https://myfaqs.onrender.com
- Admin Username: Sonugupta
- Admin Password: 12345
---

## Features

- **Authentication**: APIs involving Create, Read, Update, and Delete functionalities for managing FAQs are restricted to Admin Only, while the ReadOnly APIs are accessible to normal user.
- **Multi-language Support**: The application automatically translates FAQs into defined top-5 languages (Spanish, Hindi, French, German, Chinese Simplified) at the moment it is created, and the remaining languages are translated dynamically on the user request. It will improve the response for accessing the FAQs in popular languages by pre-translating them and storing them in db/cache memory.
- **Messaging Queues**: ***Redis Queue Worker*** is used as message queues for off-loading the translation of FAQs in top-5 languages. This keeps the **main thread** unblocked and responsive while the translation tasks are processed in the **background** Asynchronously.
- **Cache Mechanism**: Redis is used as **Cache Store**, which stores the frequently accessed FAQs making responses faster and efficient.
- **Admin Interface**: The admin panel contains a WYSIWYG editor to format FAQs question-answers, along with **searching**, **sorting**, and **pagination** features.
- **Custom Logging**: Detailed logging setup to monitor application behavior and capture errors.
- **Security**:
  - **CSRF** protection and secure cookies.
  - **Rate limiting** to prevent abuse.

---

## Issues
- Google translate API seems to have a rigid **rate limiting** and **throttling** mechanism. When I was testing locally, my translation requests was denied getting an **HTTP 429** response. So some APIs, specifically those which involves accessing the translated FAQs are facing a significant delay in production.
- Although I've tried to implement **sleep/delays** between consecutive google API requests and **retry mechanism**, the issue still seems to persist. Hence, some unit tests which were supposed to cover these endpoints are also affected and are getting failed.
- I considered trying other translation services like MS Azure, Amazon AWS translate, IBMs etc. but they were mostly paid and even setting up a free account required verified payment informations, which I cant provide at this moment.

Considering these issues, I request to the evaluation team to please review the code instead of directly trying to tests those API endpoints in production. I have tried my best to implement them and I hope the efforts would be equally considered.

---

## Setup Instructions

### Prerequisites

- **Python 3.12**
- **Redis Server**

### Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/Sonugupta2001/myFAQs.git
   cd MyFAQProject
   ```

2. **Create a Virtual Environment**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
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
   This will start the rq worker in background for processing async translation tasks.

4. **Access the Application**

   - **Admin Interface**: [http://localhost:8000/admin/](http://localhost:8000/admin/)
   - **API Endpoints**: [http://localhost:8000/api/faqs/](http://localhost:8000/api/faqs/)

---

## API Endpoints

#### 1. List FAQs

Retrieve a list of all FAQs.

- **URL**: `/api/faqs/`
- **Method**: `GET`
- **Query Parameters**:
  - `lang` (optional): `en`, `es`, `hi`, `fr`, `de`, `zh_cn`
  - Default: `en`.

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
  - `lang` (optional): `en`, `es`, `hi`, `fr`, `de`, `zh_cn`
  - Default: `en`.

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
  

#### 4.[Admin Only] Update FAQ

Update an existing FAQ.

- **URL**: `/api/faqs/<id>/`
- **Method**: `PATCH`
- **Headers**:
  - `Authorization: Token <admin_token>`

- **Request Body**:

  ```json
  {
      "question": "What is the Django Framework?",
      "answer": "Django is a high-level Python web framework."
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


| Status Code             | Description                                                                                   | Example Response                                           |
|-------------------------|-----------------------------------------------------------------------------------------------|------------------------------------------------------------|
| `400 Bad Request`       | Invalid input data.                                                                           | `{"detail": "Invalid data."}`                              |
| `401 Unauthorized`      | Authentication credentials were not provided or are invalid.                                  | `{"detail": "Authentication credentials were not provided."}` |
| `403 Forbidden`         | User does not have permission to perform the action.                                         | `{"detail": "You do not have permission to perform this action."}` |
| `404 Not Found`         | The requested resource does not exist.                                                       | `{"detail": "Not found."}`                                 |
| `405 Method Not Allowed`| HTTP method not supported for the endpoint.                                                  | `{"detail": "Method \"PUT\" not allowed."}`                |
| `500 Internal Server Error`| An unexpected error occurred on the server.                                                  | `{"detail": "Internal server error."}`                     |

---

## License

This project is licensed under the [MIT License](LICENSE).

---
